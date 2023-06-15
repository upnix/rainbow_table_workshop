from RainbowTables import HashSearch, KeySpace, hash_reduce
from Key_Space_Widgets import ks_get_keyspace

import ipywidgets as widgets


def rbt_genKey_callback(keyspace):
    rbt_key_Text.value = keyspace.generate_key()[0]
    

def rbt_hashAlgo_callback(hash_str, key, text_widget):
    hash_func = HashSearch.get_hash_func(hash_str)
    text_widget.value = hash_func(key)
    
def rbt_reduceKey_callback(digest, keyspace, text_widget):
    text_widget.value = hash_reduce(digest, 0, keyspace.key_size, keyspace.allowable_chars, keyspace.allow_smaller_keys)

common_layout_width = '200px'
    
rbt_genKey_Button = widgets.Button(description='Generate key')
rbt_genKey_Button.on_click(lambda b: rbt_genKey_callback(ks_get_keyspace()))
rbt_genKey_Button.layout.width = common_layout_width

rbt_key_Text = widgets.Text()
rbt_key_Text.layout.width = common_layout_width

rbt_key_VBox = widgets.VBox([
    rbt_genKey_Button,
    rbt_key_Text
])


rbt_hashAlgo_Button = widgets.Button(description='Use this hash algo.')
rbt_hashAlgo_Button.on_click(lambda b: rbt_hashAlgo_callback(rbt_hashAlgo_Dropdown.value, rbt_key_Text.value, rbt_reduceKey_Text))
rbt_hashAlgo_Button.layout.width = common_layout_width

rbt_hashAlgo_Dropdown = widgets.Dropdown(
    options = HashSearch.HASH_ALGORITHMS,
    value = HashSearch.HASH_ALGORITHMS[0]
)
rbt_hashAlgo_Dropdown.layout.width = common_layout_width


rbt_hashAlgo_layout = widgets.VBox([
    rbt_hashAlgo_Button,
    rbt_hashAlgo_Dropdown
])


rbt_key2_Text = widgets.Text()
rbt_key2_Text.layout.width = common_layout_width

rbt_key2_layout = widgets.VBox([
    widgets.Label(value='Key from hash digest reduction'),
    rbt_key2_Text],
    layout=widgets.Layout(align_items='center'))


rbt_reduceKey_Button = widgets.Button(description='Apply reduction')
rbt_reduceKey_Button.on_click(lambda b: rbt_reduceKey_callback(rbt_reduceKey_Text.value, ks_get_keyspace(), rbt_key2_Text))
rbt_reduceKey_Button.layout.width = common_layout_width

rbt_reduceKey_Text = widgets.Text()
rbt_reduceKey_Text.layout.width = common_layout_width

rbt_reduceKey_layout = widgets.VBox([
    rbt_reduceKey_Button,
    rbt_reduceKey_Text])


def hash_reduce_chain_display():
    display(widgets.HBox([
        rbt_key_VBox,
        rbt_hashAlgo_layout,
        rbt_reduceKey_layout,
        rbt_key2_layout
    ]))