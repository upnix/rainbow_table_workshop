import random
import string
import hashlib
import sys
import time
import re

def descriptive_time(time_in_seconds):
    est_time = time_in_seconds
    time_est_list = list()

    time_est_list.append(('years', int(est_time // 31536000)))
    est_time -= (31536000 * time_est_list[-1][1])

    time_est_list.append(('months', int(est_time // 2592000)))
    est_time -= (2592000 * time_est_list[-1][1])

    time_est_list.append(('weeks', int(est_time // 604800)))
    est_time -= (604800 * time_est_list[-1][1])

    time_est_list.append(('days', int(est_time // 86400)))
    est_time -= (86400 * time_est_list[-1][1])

    time_est_list.append(('hours', int(est_time // 3600)))
    est_time -= (3600 * time_est_list[-1][1])

    time_est_list.append(('minutes', int(est_time // 60)))
    est_time -= (60 * time_est_list[-1][1])

    time_est_list.append(('seconds', int(est_time)))

    time_est_string = str()
    for key, value in time_est_list:
        started_output = False

        if value > 0 or started_output or key == 'seconds':
            started_output = True
            time_est_string += str(value) + " " + key
            if key != 'seconds':
                time_est_string += ", "

    return time_est_string


# A reduction function
def hash_reduce(hash_digest, salt, key_length, allowable_chars):
    hash_in_binary = str()

    for c in hash_digest:
        hash_in_binary += bin(ord(c))[2:].zfill(8)
        
    binary_chunks = int(len(hash_in_binary)/key_length)
    key_from_hash = str()
    for i in range(0, key_length):
        left_bound = i*binary_chunks
        right_bound = (i+1)*binary_chunks
        if i == (key_length-1):
            right_bound = len(hash_in_binary)
        list_pos = int(hash_in_binary[left_bound:right_bound], 2)%len(allowable_chars)
        key_from_hash += allowable_chars[list_pos]
        
    return key_from_hash

class HashSearch:
    HASH_ALGORITHMS = list(['md5', 'sha1', 'sha256', 'sha512', 'shake_128', 'blake2b', 'Shorty hash'])
    key_hash_dict = dict()
    
    def __init__(self, keyspace, hash_algorithm):
        self.keyspace = keyspace
        self.hash_algorithm = hash_algorithm
        # This was a trick I found here: https://stackoverflow.com/a/28766809
        self.search_keyspace = self._instance_search_keyspace
    
    def save_hashed_keyspace(self, size=0, force=False):
        # Don't do it if...
        if not force and (
            (len(self.key_hash_dict) == self.keyspace.size() and size == 0) or
            (len(self.key_hash_dict) == size and size != 0)
        ):
            return

        
        hash_algo = HashSearch.get_hash_func(self.hash_algorithm)
        
        self.key_hash_dict.clear()
        
        def generate(key, hash_algo, key_hash_dict):
            key_hash_dict[key] = hash_algo(key)
        
        self.keyspace.keyspace_operation(lambda k: generate(k, hash_algo, self.key_hash_dict), size)
        
    
    def estimated_search_stats(self):
        # Contents of returned list
        # * Time to generate key space once
        # * Time to find a key in the key space
        # * Memory required to save entire hashed key space
        # * Time to find key in saved hashed key space
        
        if self.keyspace.size() > 1000:
            # Create a dict of key:hash pairs that's only 1000 elements long
            start_time = time.time()
            small_hashed_keyspace = self.keyspace.generate_hashed_keyspace(
                self.hash_algorithm, 1000)
            est_time = (self.keyspace.size() / 1000)*(time.time() - start_time)
            est_size = (self.keyspace.size() / 1000)*sys.getsizeof(small_hashed_keyspace)
        else:
            est_time = 0
            est_size = 0
                   
        #print(est_time, "from ", str(len(small_hashed_keyspace)))

        # Terabyte or bigger
        size_string = str()
        if est_size >= 1099511627776:
            size_string = str(round(est_size / 1099511627776, 2)) + " terabytes"

        elif est_size >= 1073741824:
            size_string = str(round(est_size / 1073741824, 2)) + " gigabytes"

        else:
            size_string = str(round(est_size / 1048576, 2)) + " megabytes"
            
        gen_entire_keyspace_time = descriptive_time(est_time)
        search_half_keyspace_time = descriptive_time(est_time//2)
        
        return list([gen_entire_keyspace_time, search_half_keyspace_time, size_string, 'Fast?'])


    def search_saved_keyspace(self, hash_digest):
        results = list()
        for key, value in self.key_hash_dict.items():
            if value in hash_digest:
                results.append((key, value))
        
        return results
    
    @staticmethod
    def get_hash_func(hash_algo_str):
        if hash_algo_str == 'md5':
            return lambda k: hashlib.md5(k.encode('ascii')).hexdigest()
        elif hash_algo_str == 'sha1':
            return lambda k: hashlib.sha1(k.encode('ascii')).hexdigest()
        elif hash_algo_str == 'sha256':
            return lambda k: hashlib.sha256(k.encode('ascii')).hexdigest()
        elif hash_algo_str == 'sha512':
            return lambda k: hashlib.sha512(k.encode('ascii')).hexdigest()
        elif hash_algo_str == 'shake_128':
            return lambda k: hashlib.shake_128(k.encode('ascii')).hexdigest(128)
        elif hash_algo_str == 'blake2b':
            return lambda k: hashlib.blake2b(k.encode('ascii')).hexdigest()
        elif hash_algo_str == 'Shorty hash':
            return lambda k: hashlib.md5(k.encode('ascii')).hexdigest()[:6]
        else:
            return -1

    def _instance_search_keyspace(self, digest_str):
        return HashSearch.search_keyspace(self.keyspace, digest_str, self.hash_algorithm)

    @staticmethod
    def search_keyspace(keyspace, digest_str, hash_algo_str):
        hash_algo = HashSearch.get_hash_func(hash_algo_str)
        key_hash_pair = list()
        
        def search(key, hash_digest, hash_algorithm, match_list):
            if hash_digest == hash_algorithm(key):
                match_list.append((key, hash_algorithm(key)))
        
        keyspace.keyspace_operation(lambda k: search(k, digest_str, hash_algo, key_hash_pair))

        return key_hash_pair


class KeySpace:
    PREBUILT_CHAR_LIST = list(['0-9 (10 chars)',
             'a-z (26 chars)',
             'A-Z (26 chars)',
             'Special characters (32 chars)',
             'Hexadecimal* (16 chars)'])
    
    key_operation_count = 0
    
    def __init__(self, key_size, allowable_characters, allow_smaller_keys):
        self.key_size = key_size
        
        # Rebuild the passed 'allowable_characters' list, looking for any items
        # from 'PREBUILT_CHAR_LIST'
        self.allowable_chars = list()
        for e in allowable_characters:
            if e in self.PREBUILT_CHAR_LIST:
                # Expand
                self.allowable_chars.extend(
                    KeySpace.expand_prebuilt_char(e))
            else:
                self.allowable_chars.append(e)
        self.allowable_chars = list(set(self.allowable_chars))
        
        self.allow_smaller_keys = allow_smaller_keys
        # This was a trick I found here: https://stackoverflow.com/a/28766809
        self.size = self._instance_size
    
    @staticmethod
    def expand_prebuilt_char(prebuilt_allowable_char):
        # An empty list of the allowable characters, which we'll be adding to
        expanded_allowable_chars = list()

        # For each of the options the user could have selected for
        # 'allowableCharacters_widget'...
        # ... if they selected digits 0 through 9...
        if prebuilt_allowable_char[:3] == '0-9':
            # ... add to the 'expanded_allowable_chars' list the digits
            # 0 through 9
            expanded_allowable_chars.extend([str(i) for i in range(0,10)])

        # ... if they selected lowercase letters...
        elif prebuilt_allowable_char[:3] == 'a-z':
            # ... add to the 'expanded_allowable_chars' list all
            # lowercase letters
            expanded_allowable_chars.extend(string.ascii_lowercase)

        # ... if they selected uppercase letters...
        elif prebuilt_allowable_char[:3] == 'A-Z':
            # ... add to the 'allowable_chars' list all
            # uppercase letters
            expanded_allowable_chars.extend(string.ascii_uppercase)

        # ... if they selected "Special Characters" ...
        elif prebuilt_allowable_char[:7] == 'Special':
            # ... add to the 'expanded_allowable_chars' list what Python
            # refers to as "punctuation
            expanded_allowable_chars.extend(string.punctuation)

        # ... if they selected "Hexadecimal" ...
        elif prebuilt_allowable_char[:4] == 'Hexa':
            # ... add to the 'expanded_allowable_chars' list lowercase hex
            # characters.
            expanded_allowable_chars.extend(string.hexdigits[:16])
            # Remove any duplicates created by the hex characters overlapping
            # with other selected characters
            expanded_allowable_chars = list(set(expanded_allowable_chars))

        # ... if they selected none of those things, then...
        else:
            print("Something has gone wrong...")

        # Return to the caller of this function the list we built of all
        # allowable characters the user selected
        return expanded_allowable_chars
    
    def key_exists(self, search_key):
        # Keep track of whether we found an error while running through our search
        # key checks. This is used at the end of the function to either give the
        # A-OK, or return '-1' (not A-OK)
        found_error = False

        # Is the search key longer than the max length of keys in the defined key
        # space?
        if len(search_key) > self.key_size:
            found_error = True
            print("The key you're searching for is longer than the keys " +
                  "of the key space.")

        # Is the search key shorter?
        elif (len(search_key) <= 0 or
              (len(search_key) < self.key_size and not self.allow_smaller_keys)):
            found_error = True
            print("The key you're searching for is shorter than the keys of the " +
                  "key space.")

        # Go through each character that is the provided search key and make sure
        # each falls within the range of allowable characters.
        for c in search_key:
            if c not in self.allowable_chars:
                found_error = True
                print("Character found in search key that doesn't exist in " +
                      "allowable character list:", c)

                # 'break' doesn't quit the function like 'return' would, but it
                # will exit the loop that it's contained in (after finding one
                # character that's not allowed, lets just not bother to check the
                # rest) 
                break

        if not found_error:
            print("You're good to go! This key should exist in your " +
                  "defined key space!")
            return 1
        else:
            return -1

    def keyspace_operation(self, operation_func, size = 0):
        self.key_operation_count = 0
        if self.allow_smaller_keys:
            for i in range(0, self.key_size):
                self._keyspace_operation(operation_func, str(), self.key_size-i, size)
                
        else:
            self._keyspace_operation(operation_func, str(), self.key_size, size)
        
    def _keyspace_operation(self, operation_func, built_key, position, size):
        # Loop through each allowed character in the key space.
        for c in self.allowable_chars:
            # Ensure we haven't called this function for every key position
            if position > 1:
                if self._keyspace_operation(operation_func, built_key+c, position-1, size) == True:
                    return True

            elif position == 1:
                if size != 0 and self.key_operation_count >= size:
                    return True
                operation_func(built_key+c)
                self.key_operation_count += 1

        
    def generate_keyspace(self, size = 0):
        keyspace = list()
        
        self.keyspace_operation(keyspace.append, size)
        
        return keyspace
    
    
    def generate_hashed_keyspace(self, hash_algo_str, size = 0):
        hashed_keyspace = dict()
        
        hash_algorithm = HashSearch.get_hash_func(hash_algo_str)
        # 
        if hash_algorithm == -1:
            return -1
        
        def hash_operations(key, hash_algo, hashed_keyspace_dict):
            hashed_keyspace_dict[key] = hash_algo(key)
            
        
        self.keyspace_operation(lambda k: hash_operations(k, hash_algorithm, hashed_keyspace), size)
        
        return hashed_keyspace


    def generate_key(self, num=1):
        # Don't even bother if the key space is == 0
        if self.size() <= 0:
            return -1
        
        key_list = list()
        
        key_length = self.key_size
        
        # TODO: The problem here is that keys of shorter lengths don't
        # represent an equal portion of the key space.
        for _ in range(0, num):
            key = str()
            if self.allow_smaller_keys:
                key_length = random.randint(1, self.key_size)
    
            for _ in range(0, key_length):
                key += random.choice(self.allowable_chars)
                
            key_list.append(key)

        return key_list
    
    
    def _instance_size(self):
        if self.allow_smaller_keys:
            keyspace_size = 0
            for i in range(1, self.key_size+1):
                keyspace_size += len(self.allowable_chars)**i
        else:
            keyspace_size = len(self.allowable_chars)**self.key_size
            
        return keyspace_size

    @staticmethod
    def size(key_length, num_chars, allow_smaller):
        if allow_smaller:
            keyspace_size = 0
            for i in range(1, key_length+1):
                keyspace_size += num_chars**i
        else:
            keyspace_size = num_chars**key_length
            
        return keyspace_size
    

class RainbowTable:
    def __init__(self, keyspace, chain_pairs, table_rows, reduction_func = hash_reduce, hash_func = HashSearch.get_hash_func('Shorty hash')):
        self.keyspace = keyspace
        
        self.chain_pairs = chain_pairs
        self.table_rows = table_rows
        
        self.reduction_func = lambda hd: reduction_func(hd, 0, keyspace.key_size, keyspace.allowable_chars)
        self.hash_func = hash_func
        
        self.table = list()
        self._generate_rows()
        # self.table = HTML_Table(_generate_header(pairs_in_chain))
        
        self.table_type = 'full' # 'full' or 'sparse'
        
        self.html_table = HTML_Table(self._display_header())
        
    def _display_header(self):
        table_header = list()
        for i in range(0, 2*self.chain_pairs, 2):
            table_header.extend([f'Key<br />({i})', '', f'Digest<br />({i+1})'])
            if i < 2*(self.chain_pairs-1):
                table_header.extend([''])
        return table_header

    def _generate_rows(self):
        for i in range(0, self.table_rows):
            chain = list()
            
            key = self.keyspace.generate_key()[0]
            for k in range(0, self.chain_pairs):
                digest = self.hash_func(key)
                chain.append((key, digest))

                if k < self.chain_pairs-1:
                    key = self.reduction_func(digest)

            self.table.append(chain)
    
    def display_table(self, html_output_widget, rows=5, slow=0):
        row_count = 0
        self.html_table.table_content.clear()
        for row_tuples in self.table:
            # A new table row
            self.html_table.table_content.append(list())
            for key, digest in row_tuples:
                # A new pair to the existing row
                self.html_table.table_content[-1].extend([key, '=>', digest, '=>'])
            # Remove the trailing '=>'
            self.html_table.table_content[-1].pop()
            row_count += 1
            if row_count >= rows:
                break
        html_output_widget.value = self.html_table.generate_table()


class HTML_Table:
    def __init__(self, headers = list(), rows = list()):
        self.header_row = headers
        self.table_content = rows
    
    def generate_table(self):
        i = 0
        k = 0
        table_HTML = '<table><tr>'
        for cell in self.header_row:
            table_HTML += '<th>' + cell + '</th>'
        table_HTML += '</tr>'
        for row in self.table_content:
            i += 1
            table_HTML += '<tr>'
            for cell in row:
                k += 1
                table_HTML += '<td>' + cell + '</td>'
            table_HTML += '</tr>'

        table_HTML += '</table>'

        return table_HTML
    
    def add_row(self, row_content, start_pos=0):
        new_row = [''] * len(self.header_row)
        for i in range(start_pos, len(self.header_row)):
            if len(row_content) == 0:
                break
            new_row[i] = row_content.pop(0)
        self.table_content.append(new_row)
            
    
    def emphasize(self, coord):
        new_content = '<b><i>' + self.table_content[coord[0]][coord[1]] + '</i></b>'
        self.table_content[coord[0]][coord[1]] = new_content
    
    def highlight(self, coord, color='yellow'):
        new_content = f'<span style="background-color: {color};">' + self.table_content[coord[0]][coord[1]] + '</span>'
        self.table_content[coord[0]][coord[1]] = new_content
        
    def remove_row(self, row):
        del self.table_content[row]
    
    def blackout_range(self, start_coord, end_coord):
        for row in range(start_coord[0], end_coord[0]+1):
            for cell in range(start_coord[1], end_coord[1]+1):
                self.highlight([row, cell], 'black')
        
        
    def clear_tags(self, start_coord, end_coord = False):
        if end_coord == False:
            end_coord = start_coord
            
        for row in range(start_coord[0], end_coord[0]+1):
            for cell in range(start_coord[1], end_coord[1]+1):
                new_content = self._remove_tags(self.table_content[row][cell])
                self.table_content[row][cell] = new_content
                
                

    
    def _remove_tags(self, html_string):
        return re.sub('<.*?>', '', html_string)