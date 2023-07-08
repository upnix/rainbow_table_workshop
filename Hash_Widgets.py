import ipywidgets as widgets
from IPython.display import display
from RainbowTables import HashSearch
import time


def hashKey_apply_callback(key, hash_algorithm,
                           hash_OutputWidget, hash_history_OutputWidget):

    hash_algo = HashSearch.get_hash_func(hash_algorithm)
    hash_digest = hash_algo(key)

    hash_OutputWidget.clear_output()
    with hash_OutputWidget:
        print(hash_digest)

    row_data = [key, hash_algorithm, hash_digest, str(len(hash_digest))]
    
    print_table_row(row_data, ['32%', '15%', '33%', '20%'], hash_history_OutputWidget, False)



def clearHistory_callback(hash_history_OutputWidget):
    hash_history_OutputWidget.clear_output()
    row_data = ['Text to hash', 'Hash algorithm',
                'Hash digest', 'Characters in digest']
    print_table_row(row_data, ['32%', '15%', '33%', '20%'], hash_history_OutputWidget, True)


def print_table_row(row_data, widths, output_widget, header=False):
    built_HBox_list = list()
    
    for i in range(0, len(row_data)):
        cell = widgets.Output(layout={'border': '1px solid black', 'width': f'{widths[i]}'})
        style = """
        <style>
            .output_wrapper .output {
                white-space: pre-wrap;
            }
        </style>
        """
        with cell:
            display(widgets.HTML(style))
            
            if isinstance(row_data[i], widgets.Widget):
                display(row_data[i])
            else:
                print(row_data[i])

        built_HBox_list.append(cell)
    
    with output_widget:
        display(widgets.HBox(built_HBox_list))
        
    time.sleep(0.5)
    

# Hashed key output - Output
hashKey_OutputWidget = widgets.Output(layout={'border': '1px solid black'})

# Hashed key output - Label over Output (VBox)
hashKey_output_VBoxWidget = widgets.VBox([
    widgets.Label(value='Hash digest produced by selected algorithm'),
    hashKey_OutputWidget],
    layout=widgets.Layout(width='40%')
)


hashKey_history_OutputWidget = widgets.Output(layout={'width': '100%'})


# Key to hash - Text
hashKey_input_TextWidget = widgets.Text(
    placeholder='Enter key to hash'
)

# Key to hash - Label over Text (VBox)
hashKey_input_VBoxWidget = widgets.VBox([
    widgets.Label(value='Enter text to hash'),
    hashKey_input_TextWidget],
    layout=widgets.Layout(width='30%')
)


# Hash algorithm for key - Dropdown
hashKey_selection_DropdownWidget = widgets.Dropdown(
    options=HashSearch.HASH_ALGORITHMS,
    value=HashSearch.HASH_ALGORITHMS[0]
)

# Hash algorithm for key - Label over Dropdown (VBox)
hashKey_selection_VBoxWidget = widgets.VBox([
    widgets.Label(value='Select hash algorithm to apply'),
    hashKey_selection_DropdownWidget],
    layout=widgets.Layout(width='30%')
)


# Apply hash algorithm - Button
hashKey_apply_ButtonWidget = widgets.Button(description='Apply hash')

# Apply hash algorithm - Button callback
hashKey_apply_ButtonWidget.on_click(
    lambda b:
        hashKey_apply_callback(
            hashKey_input_TextWidget.value,
            hashKey_selection_DropdownWidget.value, 
            hashKey_OutputWidget,
            hashKey_history_OutputWidget
        )
)


# Clear hash history - Button
hashKey_clear_ButtonWidget = widgets.Button(description='Clear history')

# Clear hash history - Button callback
hashKey_clear_ButtonWidget.on_click(lambda b:
                                   clearHistory_callback(hashKey_history_OutputWidget)
                                  )



# Layout for hashing a key
hashKey_layout_VBoxwidget = widgets.VBox([
    # Three widgets, horizontally
    widgets.HBox([hashKey_input_VBoxWidget, 
                  hashKey_selection_VBoxWidget,
                  hashKey_output_VBoxWidget]),
    # "Apply hash" and "Clear history" buttons
    widgets.HBox([hashKey_apply_ButtonWidget,
                  hashKey_clear_ButtonWidget]),
    # Output
    hashKey_history_OutputWidget
])

clearHistory_callback(hashKey_history_OutputWidget)

# Just to double check...
# display(hashKey_layout_VBoxwidget)

#######

# Reverse the hash of a two digit PIN
rvPIN_OutputWidget = widgets.Output(layout={'border': '1px solid black', 'width': '100%', 'height': '200px', 'overflow_y':'auto'})
rvPIN_OutputWidget.box_id = f"output_widget_{id(rvPIN_OutputWidget)}"

print_table_row(['Key to hash', 'Hash algorithm', 'Digest comparison'],
                ['33%', '33%', '33%'],
                rvPIN_OutputWidget,
               True)

def rvPIN_IntTextWidget_callback(int_input, input_hash, hash_algorithm, output_widget):
    input_key = str(f"{int_input.new:02d}")
    hash_algo = HashSearch.get_hash_func(hash_algorithm)
    result_hash_digest = hash_algo(input_key)
    
    digest_compare_str = str()
    if input_hash == result_hash_digest:
        digest_compare_str = input_hash + ' ==\n' + result_hash_digest + ' (MATCH!)'
    else:
        digest_compare_str = input_hash + ' !=\n' + result_hash_digest + ' (No match)'

    print_table_row([input_key, hash_algorithm, digest_compare_str],
                    ['33%', '33%', '33%'],
                    output_widget,
                    False)

    
def resetSearch_callback(input_widget, hash_Dropdown_widget, PIN_int_widget, rvPIN_OutputWidget):
    input_widget.value = ''
    hash_Dropdown_widget.value = 'md5'
    PIN_int_widget.value=0
    rvPIN_OutputWidget.clear_output()
    print_table_row(['Key to hash', 'Hash algorithm', 'Digest comparison'],
                    ['33%', '33%', '33%'],
                    rvPIN_OutputWidget,
                    True)
    

# Reverse PIN digest - Text
rvPIN_digest_TextWidget = widgets.Text(placeholder='Enter hash')
rvPIN_digest_TextWidget.style.description_width = 'initial'


# Hash algorithm of digest - Dropdown
rvPIN_selection_DropdownWidget = widgets.Dropdown(
    options=HashSearch.HASH_ALGORITHMS,
    value=HashSearch.HASH_ALGORITHMS[0]
)


rvPIN_IntTextWidget = widgets.BoundedIntText(
    value=0,
    min=0,
    max=99
)

rvPIN_IntTextWidget.observe(
    lambda c: rvPIN_IntTextWidget_callback(c,
                            rvPIN_digest_TextWidget.value,
                            rvPIN_selection_DropdownWidget.value,
                            rvPIN_OutputWidget),
    names='value')


# Reverse PIN reset history - Button
rvPIN_reset_ButtonWidget = widgets.Button(description='Reset search')

# Reverse PIN reset history - Button callback
rvPIN_reset_ButtonWidget.on_click(
    lambda b: resetSearch_callback(rvPIN_digest_TextWidget,
                                   rvPIN_selection_DropdownWidget,
                                   rvPIN_IntTextWidget,
                                   rvPIN_OutputWidget)
)

rvPIN_layout = widgets.VBox([
    widgets.HBox([
        widgets.VBox([
            widgets.Label(value="Hash you'd like to reverse"),
            rvPIN_digest_TextWidget
        ]),
        widgets.VBox([
            widgets.Label(value="Hash algorithm to apply"),
            rvPIN_selection_DropdownWidget
        ]),
        widgets.VBox([
            widgets.Label(value="Choose PIN to hash and compare"),
            rvPIN_IntTextWidget
        ]),
        rvPIN_reset_ButtonWidget
    ]),
    rvPIN_OutputWidget
])

resetSearch_callback(rvPIN_digest_TextWidget,
                     rvPIN_selection_DropdownWidget,
                     rvPIN_IntTextWidget,
                     rvPIN_OutputWidget)

# Just to double check...
#display(rvPIN_layout)


def hash_display():
    display(hashKey_layout_VBoxwidget)

    
def reverse_PIN_display():
    display(rvPIN_layout)
