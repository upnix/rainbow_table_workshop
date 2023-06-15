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
# TODO: I don't really want to run this until they user is looking at the tab
#st_generate_display(st_selection_DropdownWidget, st_display_OutputWidget)

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


st_digests_and_buttons_layout = widgets.HBox([
    st_digests_VBoxWidget,
    widgets.VBox([st_generate_layout, st_search_layout])])




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
