from RainbowTables import KeySpace, HashSearch
from Key_Space_Widgets import ks_define_layout, ks_get_keyspace, ks_get_OutputWidget
from RainbowTables import HTML_Table
from Hash_Widgets import print_table_row
import ipywidgets as widgets
from IPython.display import display
import string
import sys
import time

###
# Adds a new row to the HTML "saved table"
###
def ts_saved_table_row(saved_tables):
    saved_row = saved_tables[-1]
    
    # Generate key space information string
    ks_info_str = "<b>Key size:</b> "
    if saved_row[0].allow_smaller_keys == True:
        ks_info_str += "<= "
        
    ks_info_str += str(saved_row[0].key_size) + "<br />"
    
    ks_info_str += "<b>Allowed chars:</b><br />"
    for allowed_char in saved_row[0].original_allowed_chars:
        ks_info_str += "&nbsp;&nbsp;* " + allowed_char + "<br />"
    
    
    # Generate the "Size" information string
    ks_size_str = f"<b>Total keys:</b> {saved_row[0].size():,}<br />"
    table_size = sys.getsizeof(saved_row[1].key_hash_dict)
    size_string = '<b>Size in memory: </b>'
    if table_size >= 1099511627776:
        size_string += str(round(table_size / 1099511627776, 2)) + " terabytes"

    elif table_size >= 1073741824:
        size_string += str(round(table_size / 1073741824, 2)) + " gigabytes"

    else:
        size_string += str(round(table_size / 1048576, 2)) + " megabytes"
    ks_size_str += size_string
    
    return [str(len(saved_tables)), ks_info_str, saved_row[1].hash_algorithm, ks_size_str]


###
# Adds the only row to the HTML "dynamic table"
###
def ts_dyn_table_row(keyspace, hash_algo):
    if keyspace == None:
        return ['No key space defined!', '']

    # Generate key space information string
    ks_info_str = "<b>Key size:</b> "
    if keyspace.allow_smaller_keys == True:
        ks_info_str += "<= "
        
    ks_info_str += str(keyspace.key_size) + "<br />"
    
    ks_info_str += "<b>Allowed chars:</b><br />"
    for allowed_char in keyspace.original_allowed_chars:
        ks_info_str += "&nbsp;&nbsp;* " + allowed_char + "<br />"
    
    
    # Generate the "Size" information string
    hashsearch = HashSearch(keyspace, hash_algo)
    generation_stats = hashsearch.estimated_search_stats()
    ks_size_str = f"<b>Total keys:</b> {keyspace.size():,}<br />"
    ks_size_str += '<b>Estimated...</b><br />'
    ks_size_str += "&nbsp;&nbsp;*<em>Table generation time:</em> " + generation_stats[0] + "<br />"
    ks_size_str += "&nbsp;&nbsp;*<em>Search time:</em> " + generation_stats[1] + "<br />"
    ks_size_str += "&nbsp;&nbsp;*<em>Size in memory:</em> " + generation_stats[2]
        
    return [ks_info_str, ks_size_str]


#####
# CALLBACKS
#####
def ts_saved_search_callback(saved_tables, table_id, digest_text, status_output):
    digest_list = digest_text.split("\n")
    
    with status_output:
        # Check the user provided a saved table ID
        if (not isinstance(table_id, int) or
            table_id < 0 or
            table_id > len(saved_tables)):
            print("Please select an ID for a saved table before searching.")
            return

        # Check the user supplied a hash digest
        if len(digest_text) < 6:
            print("Please provide at least one hash digest to search for.")
            return
        
        for digest in digest_list:
            hashsearch = saved_tables[table_id-1][1]
            print("\n-- Starting search of saved key:digest table --")
            search_start = time.time()
            result = hashsearch.search_saved_keyspace(digest)
            print(result)
            print(str(int(time.time() - search_start)), "s: Search complete")
            

def ts_dyn_search_callback(digest_list, hash_algo, status_output):
    ks = ks_get_keyspace()

    digest_list = digest_list.split("\n")
    
    with status_output:
        if ks == None:
            print("** Please define a key space first! **")

        elif len(digest_list[0]) <= 0:
            print("** Please provide at least one hash digest! **")

        else:
            for digest in digest_list:
                hashsearch = HashSearch(ks, hash_algo)
                # hashsearch.search_keyspace(digest, 10)
                hashsearch.search_keyspace(digest)
            
            
def ts_hash_select_callback(html_table, hash_algo, table_output):
    if len(html_table.table_content) > 0:
        html_table.remove_row(-1)
        html_table.add_row(ts_dyn_table_row(ks_get_keyspace(), hash_algo))
    
    table_output.clear_output()
    with table_output:
        display(widgets.HTML(html_table.generate_table(border=True)))
        

def ts_generate_callback(html_table, hash_algo, saved_tables, id_dropdown_widget, table_output, status_output):
    # Create the table
    ks = ks_get_keyspace()

    with status_output:
        if ks == None:
            print("** You must define a key space before generating it **")
            return

        hash_search = HashSearch(ks, hash_algo)

        print("\n-- Generating saved key:digest table --")
        search_start = time.time()
        hash_search.save_hashed_keyspace()
        print(str(int(time.time() - search_start)), "s:", ks.size(), "key:digest pairs generated.")
        print(str(int(time.time() - search_start)), "s: Table saved")

        # Save the table
        saved_tables.append([ks, hash_search])

        # Add information about the table to the HTML output
        html_table.add_row(ts_saved_table_row(saved_tables))

        table_output.clear_output()
    with table_output:
        display(widgets.HTML(html_table.generate_table(border=True)))

    id_dropdown_widget.options = [i for i in range(1, len(saved_tables)+1)]
    

def ts_reset_callback(digest_text_widget, status_output, saved_table_output,
                      html_table, saved_tables, id_dropdown_widget):
    digest_text_widget.value = ''
    
    status_output.clear_output()
    status_output.append_stdout("--- Search status ---\n")
    
    saved_tables.clear()
    
    html_table.table_content.clear()
    
    saved_table_output.clear_output()
    
    with saved_table_output:
        if len(saved_html_table.table_content) <= 0:
            print("--- No tables currently saved! ---\n\n")
    
        else:
            display(widgets.HTML(saved_html_table.generate_table(border=True)))
        
    id_dropdown_widget.options = list()


def tab_select_callback(change, html_table, hash_algo, table_output):
    if change['new'] == 1:
        ts_hash_select_callback(html_table, hash_algo, table_output)
    

# Saved tables of key:hash pairs
digest_tables = list()


# Collecting hashes we're searching for
ts_digests_TextareaWidget = widgets.Textarea(
    placeholder='86fb269d190d2c85f6e0468ceca42a20'
)

# Target hash digests to search - Label over Textarea (VBox)
ts_digests_layout = widgets.VBox([
    widgets.Label(value='Enter hash digests to search for, one per line:'),
    ts_digests_TextareaWidget
])


# Search status output - This is displayed outside of the tabbed areas. Check
# out `hs_display()`
ts_status_output = widgets.Output(layout={'border': '1px solid black', 'width': '100%'})
ts_status_output.append_stdout("--- Search status ---\n")

###
# For the "Saved Key:Digest tables"
###
# Build the table of saved digest tables
ts_saved_table_OutputWidget = widgets.Output(layout={'width': '99%'})


# Heading for the table
ts_saved_table_heading_HTML = widgets.HTML("""
<style>
.heading-text {
    font-size: 1.2em;
    font-weight: bold;
    font-style: italic;
}
</style>
<p class="heading-text">Saved Key:Digest tables</p>
                                           """)

# The 'HTML_Table' object of saved key:hash tables
saved_html_table = HTML_Table(['ID', 'Key space', 'Hash algo.',   'Size'],
                              list(),
                              ['5',   '45',        '15',           '35'])

with ts_saved_table_OutputWidget:
    if len(saved_html_table.table_content) <= 0:
        print("--- No tables currently saved! ---\n\n")

    else:
        display(widgets.HTML(saved_html_table.generate_table(border=True)))


# Create ID selection drop down
ts_id_DropdownWidget = widgets.Dropdown(
#    options=[i for i in range(0, len(digest_tables)+1)]
    options=list()
)
ts_id_DropdownWidget.layout.width = '50px'

ts_id_layout = widgets.HBox([
    widgets.Label(value='Select ID of saved table to search:'),
    ts_id_DropdownWidget
    ])


# Button to search selected key space
ts_saved_search_Button = widgets.Button(description='Search')

ts_saved_search_Button.on_click(lambda b:
                          ts_saved_search_callback(
                              digest_tables,
                              ts_id_DropdownWidget.value,
                              ts_digests_TextareaWidget.value,
                              ts_status_output
                              ))


ts_saved_layout = widgets.VBox([
    ts_saved_table_heading_HTML,
    ts_saved_table_OutputWidget,
    widgets.HBox([
        ts_id_layout, ts_saved_search_Button])
    ])


###
# For the "on-the-fly" table
###
# Heading for the table
ts_dyn_table_heading_HTML = widgets.HTML("""
<p class="heading-text">On-the-fly search</p>
                                           """)

ts_dyn_table_OutputWidget = widgets.Output(layout={'width': '75%'})


# Create dynamic table
temp_row = ts_dyn_table_row(ks_get_keyspace(), HashSearch.HASH_ALGORITHMS[0])
dynamic_html_table = HTML_Table(['Key space', 'Table stats'],
                                [temp_row],
                                ['50', '50'])


with ts_dyn_table_OutputWidget:
    display(widgets.HTML(dynamic_html_table.generate_table(border=True)))


# Hash algorithm to use - Dropdown
ts_hash_select_DropdownWidget = widgets.Dropdown(
    options=HashSearch.HASH_ALGORITHMS,
    value=HashSearch.HASH_ALGORITHMS[0]
)

ts_hash_select_DropdownWidget.layout.width = '100px'
ts_hash_select_DropdownWidget.observe(lambda d: ts_hash_select_callback(
    dynamic_html_table,
    ts_hash_select_DropdownWidget.value,
    ts_dyn_table_OutputWidget), 'value')


ts_hash_select_layout = widgets.VBox([
    widgets.Label(value='Hash algorithm:'),
    ts_hash_select_DropdownWidget])


# Button to generate defined key space
ts_generate_Button = widgets.Button(description='Generate')
ts_generate_Button.on_click(lambda b:
                            ts_generate_callback(
                                saved_html_table,
                                ts_hash_select_DropdownWidget.value,
                                digest_tables,
                                ts_id_DropdownWidget,
                                ts_saved_table_OutputWidget,
                                ts_status_output
                                ))

    
# Button to search selected key space
ts_dyn_search_Button = widgets.Button(description='Search')

ts_dyn_search_Button.on_click(lambda b:
                          ts_dyn_search_callback(                
                              ts_digests_TextareaWidget.value,
                              ts_hash_select_DropdownWidget.value,
                              ts_status_output
                              ))

ts_dynamic_layout = widgets.VBox([
    ts_dyn_table_heading_HTML,
    widgets.HBox([
        ts_dyn_table_OutputWidget,
        ts_hash_select_layout,
        widgets.VBox([ts_generate_Button, ts_dyn_search_Button])
    ])
])
    
#########
###
# This is to go below both search tables
###

# Button to reset all saved tables
ts_reset_Button = widgets.Button(description='Reset')

ts_reset_Button.on_click(lambda b:
                          ts_reset_callback(
                              ts_digests_TextareaWidget,
                              ts_status_output,
                              ts_saved_table_OutputWidget,
                              saved_html_table,
                              digest_tables,
                              ts_id_DropdownWidget
                              ))
    
ts_reset_layout = widgets.HBox([
    widgets.Label(value='Reset everything, including saved tables'),
    ts_reset_Button])


ts_hash_reverse_layout = widgets.HBox([
    ts_digests_layout,
    ts_reset_layout])


ts_layout = widgets.VBox([
    ts_saved_layout,
    widgets.HTML('<hr />'),
    ts_dynamic_layout,
    widgets.HTML('<hr />'),
    ts_hash_reverse_layout
])

rvHash_tab_widget = widgets.Tab(children=[
    ks_define_layout(),
    ts_layout]
)
rvHash_tab_widget.set_title(0, 'Define the key space')
rvHash_tab_widget.set_title(1, 'Define the hash search')

rvHash_tab_widget.observe(lambda si: tab_select_callback(
    si,
    dynamic_html_table,
    ts_hash_select_DropdownWidget.value,
    ts_dyn_table_OutputWidget), 'selected_index')


def hs_display():

    instructions_str = """
<style>
.dense-list li {
  margin-bottom: -10px;
}
</style>
<p style="line-height: 0;"><em><b>Define the key space</b></em> - In the first tab we're setting key
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
your own hash digests, then reverse them here.</p>
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
    display(rvHash_tab_widget, ts_status_output)
    
