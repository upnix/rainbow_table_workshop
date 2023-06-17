from RainbowTables import KeySpace, HashSearch
from Key_Space_Widgets import ks_define_layout, ks_get_keyspace, ks_get_OutputWidget
from Hash_Widgets import print_table_row
import ipywidgets as widgets
import string
import sys

###
# Manage the creation and deletion of saved key:digest tables
###
digest_tables = list()

def st_generate_display(hash_dropdown_widget, table_output_widget):
    table_output_widget.clear_output()
    print_table_row(['ID', 'Key space', 'Hash algo.',   'Size', 'Type'],
                    ['5%', '35%',      '15%',          '25%',  '20%'],
                    table_output_widget,
                    True)

    i = 0

    for table in digest_tables:
        # Generate key space information string
        ks_info_str = "Key size: "
        if table[0].allow_smaller_keys == True:
            ks_info_str += "<= "
            
        ks_info_str += str(table[0].key_size) + "\n"
        
        ks_info_str += "Allowed chars:\n"
        for allowed_char in table[0].original_allowed_chars:
            ks_info_str += " * " + allowed_char + "\n"
        
        
        # Generate the "Size" information string
        ks_size_str = f"Keys: {table[0].size():,}\n"
        table_size = sys.getsizeof(table[1].key_hash_dict)
        size_string = str()
        if table_size >= 1099511627776:
            size_string = str(round(table_size / 1099511627776, 2)) + " terabytes"

        elif table_size >= 1073741824:
            size_string = str(round(table_size / 1073741824, 2)) + " gigabytes"

        else:
            size_string = str(round(table_size / 1048576, 2)) + " megabytes"
        ks_size_str += size_string
        
        print_table_row([str(i),
                         ks_info_str,
                         table[1].hash_algorithm,
                         ks_size_str, 'Saved table'],
                        ['5%', '35%', '15%', '25%', '20%'],
                        table_output_widget)
        i += 1
        
    # End table with currently selected key space
    ks = ks_get_keyspace()
    # Generate key space information string
    ks_info_str = "Key size: "
    if ks.allow_smaller_keys == True:
        ks_info_str += "<= "
        
    ks_info_str += str(ks.key_size) + "\n"
    
    ks_info_str += "Allowed chars:\n"
    for allowed_char in ks.original_allowed_chars:
        ks_info_str += " * " + allowed_char + "\n"
    
    
    # Generate the "Size" information string
    hashsearch = HashSearch(ks, hash_dropdown_widget.value)
    generation_stats = hashsearch.estimated_search_stats()
    ks_size_str = f"Keys: {ks.size():,}\n"
    ks_size_str += "Table generation time: " + generation_stats[0] + "\n"
    ks_size_str += "Est. search time: " + generation_stats[1] + "\n"
    ks_size_str += "Est. size: " + generation_stats[2]

    print_table_row([str(i),
                     ks_info_str,
                     hash_dropdown_widget,
                     ks_size_str, 'Generated on demand (not saved)'],
                    ['5%', '35%', '15%', '25%', '20%'],
                    table_output_widget)

def st_generate_callback(keyspace, hash_dropdown_widget, selection_dropdown_widget, table_output_widget):
    hash_search = HashSearch(keyspace, hash_dropdown_widget.value)
    hash_search.save_hashed_keyspace()
    digest_tables.append([keyspace,hash_search])
    
    # Regenerate list of tables, somehow
    st_generate_display(hash_dropdown_widget, table_output_widget)
    
    selection_dropdown_widget.options = [i for i in range(0, len(digest_tables)+1)]
    

def st_search_callback(keyspace, hash_dropdown_widget, selection_dropdown_widget, digest_list, status_output):
    table_id = selection_dropdown_widget.value
    digest_list = digest_list.split("\n")
    
    with status_output:
        for digest in digest_list:
            if table_id < len(digest_tables):
                # We're searching a generated table
                hashsearch = digest_tables[table_id][1]
                result = hashsearch.search_saved_keyspace(digest)
                print(result)
            else:
                hashsearch = HashSearch(keyspace, hash_dropdown_widget.value)
                result = hashsearch.search_keyspace(digest)
                print(result)


def st_reset_callback(hash_dropdown_widget, selection_dropdown_widget, digest_list, status_output, table_output_widget):
    hash_dropdown_widget.value = HashSearch.HASH_ALGORITHMS[0]
    selection_dropdown_widget.options = [0]
    digest_list.value = ''
    status_output.clear_output()
    status_output.append_stdout("--- Search status ---\n")
    digest_tables.clear()
    st_generate_display(hash_dropdown_widget, table_output_widget)

def tab_refresh_table(change, hash_dropdown_widget, table_output_widget):
    if change['new'] == 1:
        st_generate_display(hash_dropdown_widget, table_output_widget)
    
    
# Hash algorithm to use - Dropdown
st_selection_DropdownWidget = widgets.Dropdown(
    options=HashSearch.HASH_ALGORITHMS,
    value=HashSearch.HASH_ALGORITHMS[0]
)

st_selection_DropdownWidget.layout.width = '100px'
st_selection_DropdownWidget.observe(lambda d: st_generate_display(st_selection_DropdownWidget, st_display_OutputWidget), 'value')

# Build the table of saved digest tables
st_display_OutputWidget = widgets.Output(layout={'width': '99%'})


# Create ID selection drop down
st_id_selection_DropdownWidget = widgets.Dropdown(
    options=[i for i in range(0, len(digest_tables)+1)]
)
st_id_selection_DropdownWidget.layout.width = '50px'

st_id_selection_layout = widgets.HBox([
    widgets.Label(value='Select ID of table for search:'),
    st_id_selection_DropdownWidget
    ])


# Collecting hashes we're searching for
st_digests_TextareaWidget = widgets.Textarea(
    placeholder='86fb269d190d2c85f6e0468ceca42a20'
)

# Target hash digests to search - Label over Textarea (VBox)
st_digests_VBoxWidget = widgets.VBox([
    widgets.Label(value='Enter hash digests to search for, one per line:'),
    st_digests_TextareaWidget
])


# Button to generate defined key space
st_generate_Button = widgets.Button(description='Generate')
st_generate_Button.on_click(lambda b:
                            st_generate_callback(
                                ks_get_keyspace(),
                                st_selection_DropdownWidget,
                                st_id_selection_DropdownWidget,
                                st_display_OutputWidget
                                ))
    
st_generate_layout = widgets.HBox([
    widgets.Label(value='Generate and save table based on current key space'),
    st_generate_Button])


# Search status output - This is displayed outside of the tabbed areas. Check
# out `hs_display()`
st_status_output = widgets.Output(layout={'border': '1px solid black', 'width': '100%'})
st_status_output.append_stdout("--- Search status ---\n")

# Button to search selected key space
st_search_Button = widgets.Button(description='Search')

st_search_Button.on_click(lambda b:
                          st_search_callback(
                              ks_get_keyspace(),
                              st_selection_DropdownWidget,
                              st_id_selection_DropdownWidget,
                              st_digests_TextareaWidget.value,
                              st_status_output
                              ))

    
st_search_layout = widgets.HBox([
    widgets.Label(value='Search based on above selection'),
    st_search_Button])


# Button to reset all saved tables
st_reset_Button = widgets.Button(description='Reset')

st_reset_Button.on_click(lambda b:
                          st_reset_callback(
                              st_selection_DropdownWidget,
                              st_id_selection_DropdownWidget,
                              st_digests_TextareaWidget,
                              st_status_output,
                              st_display_OutputWidget
                              ))

    
st_reset_layout = widgets.HBox([
    widgets.Label(value='Reset everything, including saved tables'),
    st_reset_Button])


st_digests_and_buttons_layout = widgets.HBox([
    st_digests_VBoxWidget,
    widgets.VBox([st_generate_layout, st_search_layout, st_reset_layout])])




st_layout = widgets.VBox([st_display_OutputWidget,
                          st_id_selection_layout,
                          widgets.HTML(value='<hr />'),
                          st_digests_and_buttons_layout
                          ])

keyspace_tab_widget = widgets.Tab(children=[
    ks_define_layout(),
    st_layout]
)
keyspace_tab_widget.set_title(0, 'Define the key space')
keyspace_tab_widget.set_title(1, 'Define the hash search')

keyspace_tab_widget.observe(lambda si: tab_refresh_table(si, st_selection_DropdownWidget, st_display_OutputWidget), 'selected_index')

def hs_display():

    instructions_str = """
<style>
.dense-list li {
  margin-bottom: -10px;
}
</style>
<p style="line-height: 0;"><em><b>Define a key space</b></em> - In the first tab we're setting key
restrictions that describe the types of keys allowed in the key space.</p>
<ul class="dense-list">
    <li>Keep in mind that a key space that's too large is unlikely to be
    searchable (at least in this notebook).</li>
    <li>You can see basic stats for your selected key space by clicking
    "Set key space", then going to the "Define the hash search" tab and looking
    at the last row in the table.</li>
</ul>
<br />
<p style="line-height: 0;"><em><b>Define the hash search</b></em> - In the second tab we're dealing with how we're going to search the key space that was just defined.</p>
<ul class="dense-list">
    <li>Each row of the table is a key space that can be selected to be searched.</li>
    <ul class="dense-list"><li>The bottom row always represents the <em>currently selected</em> key space, and is not a saved table.</li>
        <li>The key space and hash algorithm shown in the bottom table can be generated and saved by pressing the "Generate" button.</li>
        <li>Any rows above the last row will be key spaces that have already been generated, hashed, and saved to a table.</li>
    </ul>
    <li><em>You select which row you want to search</em> by picking the corresponding ID from the drop-down menu.</li>
    <li>The text box is where you paste in the hashes you wish to search, one per line.</li>
    <li>Make sure the table from your selected row uses the same hashing algorithm as the hash digest you're trying to reverse.</li>
</ul>
<br />
<p><em><b>Generating your own digests to reverse</b></em> -</p>
<p style="line-height: 1.5;">Use the hashing widget that's in the "Starting
notebook" (or, the same widget thats near the top of this notebook) to generate
your own hash digests, then reverse them here.'</p>
    """
    
    walkthrough_str = """
<style>
.dense-list li {
  margin-bottom: -10px;
}
</style>
<p style="line-height: 1.5;">We're going to reverse the first hash digest from
in the first row from the table above. We're told the hash digest was generated
using a key that was 3 characters in length and consisted of the characters 0
through 9. So...</p><br />
<p style="line-height: 0;"><b>In the first tab, "Define the key space"...</b></p>
<ol class="dense-list">
    <li>Select '3' as the maximum key length for the key space.</li>
    <li>Select only "0-9" as the allowable characters for the key space.</li>
    <li>"Include all keys less than max key length" can be left unchecked,
    but with such a small key length it doesn't matter much at this point.</li>
    <li>Click "Set key space"</li>
</ol>
<br />
<p style="line-height: 0;"><b>In the second tab, "Define the hash search"...</b></p>
<ol class="dense-list">
    <li>Copy the Shorty Hash digest in the table above: `17d63b`</li>
    <li>Paste this hash digest into the textbox, under where it says "Enter
    hash digests to search for"</li>
    <li>Under "Hash algo.", change the hashing algorithm to "Shorty hash."</li>
    <ol class="dense-list">
        <li>In the "Size" column you'll see information about the search you're
        about to attempt.</li>
    </ol>
    <li>You can now do one of two things (or both):</li>
    <ol class="dense-list">
        <li><em>Search</em></li>
            <ol class="dense-list">
                <li>Press the "Search" button.</li>
                <li>This will generated keys from the key space you defined, hash
                each key, then compare the resulting hash digest to the digest you
                provided.</li>
                <li>Once the hash digest is found all searching will stop. None
                of the keys or hash digests are saved.</li>
            </ol>
        <li><em>Generate *then* search</em></li>
            <ol class="dense-list">
                <li>Press the "Generate" button.</li>
                <li>This will generate keys from the key space you defined, hash
                each key, <em>and then save that key:digest pair to a table</em>.</li>
                <li>Once finished, you should now have a new row in the table,
                with details of the hashed key space you just saved.</li>
                <li>Select the table you just generated using the ID drop down menu
                (you'll probably want the ID of '0').</li>
                <li>Now click "Search."</li>
                <li>This will search for your supplied hash digest in the table
                that was saved. No key generation of hashing will take place.</li>
            </ol>
    </ol>
</ol>
    """
    
    hs_help_Accordion = widgets.Accordion(children=[widgets.HTML(instructions_str), widgets.HTML(walkthrough_str)], titles=('Instructions', 'Walkthrough'))
    display(hs_help_Accordion)
    display(keyspace_tab_widget, st_status_output)
    
    # Search summary information
    

def hs_startSearch_callback(keyspace, search_method, hash_algo, hash_digests, hs_results_Output):
    digest_list = hash_digests.split("\n")
    hashsearch = HashSearch(keyspace, hash_algo)
    with hs_results_Output:

        if search_method == 'Generate hash table, then search':
            hashsearch.save_hashed_keyspace()

            for digest in digest_list:
                result = hashsearch.search_saved_keyspace(digest)
                print(result)

        else:
            for digest in digest_list:
                result = hashsearch.search_keyspace(digest)
                print(result)
