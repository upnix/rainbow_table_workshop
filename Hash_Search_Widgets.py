from RainbowTables import KeySpace, HashSearch
from Key_Space_Widgets import ks_define_layout, ks_get_keyspace, ks_get_OutputWidget
import ipywidgets as widgets
import string

# Hash search
def hs_setSelection_callback(hash_algo, digests, search_method, digests_Output, hs_stats_Output):
    digests_Output.clear_output()
    digest_list = digests.split("\n")
    with digests_Output:
        print("Hash algorithm:", hash_algo)
        print("Hashes to search for:")
        print(digest_list)
        print("Key generation and search method:", search_method)
    
    keyspace = ks_get_keyspace()
    hashsearch = HashSearch(keyspace, hash_algo)
    with hs_stats_Output:
        search_stats = hashsearch.estimated_search_stats()
        print("Time to generate key space once:")
        print("  ", search_stats[0])
        
        print("Average time to find a key in the key space:")
        print("  ", search_stats[1])
        
        print("Memory required to save entire hashed key space:")
        print("  ", search_stats[2])
        
        print("Time to find a key in saved hashed key space:")
        print("  ", search_stats[3])


# Hash search algorithm - Dropdown
hs_selection_DropdownWidget = widgets.Dropdown(
    options=HashSearch.HASH_ALGORITHMS,
    value=HashSearch.HASH_ALGORITHMS[0]
)

# Hash search algorithm - Label over Dropdown (VBox)
hs_selection_VBoxWidget = widgets.VBox([
    widgets.Label(value='Select hash algorithm to use'),
    hs_selection_DropdownWidget
])


# Target hash digests to search - Textarea
hs_digests_TextareaWidget = widgets.Textarea(
    placeholder='86fb269d190d2c85f6e0468ceca42a20'
)

# Target hash digests to search - Label over Textarea (VBox)
hs_digests_VBoxWidget = widgets.VBox([
    widgets.Label(value='Enter hash digests to search for, one per line'),
    hs_digests_TextareaWidget
])


# Type of hash search to perform - RadioButtons
hs_SearchType_RadioWidget = widgets.RadioButtons(
    options=['Generate key space while searching', 'Generate hash table, then search'])

# Type of hash search to perform - Label over RadioButtons
hs_SearchType_VBoxWidget = widgets.VBox([
    widgets.Label(value='How would you like to generate and search the key space?'),
    hs_SearchType_RadioWidget
])


# Set hash search selections - Button
hs_setSelection_ButtonWidget = widgets.Button(description='Set selections')

hs_setSelection_ButtonWidget.on_click(lambda b:
                                      hs_setSelection_callback(
                                          hs_selection_DropdownWidget.value,
                                          hs_digests_TextareaWidget.value,
                                          hs_SearchType_RadioWidget.value,
                                          hs_selection_OutputWidget,
                                          hs_searchAdvice_OutputWidget)
                                     )


hs_selection_OutputWidget = widgets.Output(layout={'border': '1px solid black'})
hs_searchAdvice_OutputWidget = widgets.Output(layout={'border': '1px solid black'})
hs_results_OutputWidget = widgets.Output(layout={'border': '1px solid black'})

hs_layout = widgets.VBox([
    widgets.HBox([
        hs_selection_VBoxWidget,
        hs_digests_TextareaWidget,
        hs_SearchType_VBoxWidget,
        hs_setSelection_ButtonWidget])
])

# Button to start search
hs_startSearch_ButtonWidget = widgets.Button(description='Start search')

def hs_display():
    keyspace_tab_widget = widgets.Tab()
    keyspace_tab_widget.children = [
        ks_define_layout(),
        hs_layout
    ]
    keyspace_tab_widget.titles = [
        'Define the key space',
        'Define the hash search']
    
    display(keyspace_tab_widget)
    
    # Search summary information
    display(widgets.HBox([ks_get_OutputWidget(), hs_selection_OutputWidget]),
            hs_searchAdvice_OutputWidget)
    
    display(hs_startSearch_ButtonWidget)
    # Search results
    display(hs_results_OutputWidget)
    

# To start a search, I need to know about:
# * Key space details
# * Hashes to search for and the algorithm to use
#
hs_startSearch_ButtonWidget.on_click(lambda b:
                                     hs_startSearch_callback(
                                         ks_get_keyspace(),
                                         hs_SearchType_RadioWidget.value,
                                         hs_selection_DropdownWidget.value,
                                         hs_digests_TextareaWidget.value,
                                         hs_results_OutputWidget)
                                 )

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
