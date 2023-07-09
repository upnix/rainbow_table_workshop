from RainbowTables import KeySpace
# We import the Jupyter widgets module "ipywidgets," then specify that we will
# be referencing this module by the name "widgets."
#
# Because we'll be using Jupyter widgets throughout this notebook, we import
# the module at the top.
import ipywidgets as widgets

# Layout the tab that allows the user to define the key space
def ks_set_ButtonWidget_callback(keyspace, output_widget):
    output_widget.clear_output()
    with output_widget:

        print('Key size:', keyspace.key_size)
        print('Number of allowable characters:',
              len(keyspace.allowable_chars))
        print(f"Keys smaller than '{keyspace.key_size}' allowed?", keyspace.allow_smaller_keys)
        print('Size of resulting key space:', f'{keyspace.size():,}')


ks_OutputWidget = widgets.Output(layout={'border': '1px solid black'})
ks_OutputWidget.append_stdout("Select a maximum key length and the allowable characters for the key space.")

# Key space key length - IntSlider
ks_define_len_SliderWidget = widgets.IntSlider(
    value=5,
    min=1,
    max=16)

# Key space key length - Label over IntSlider (VBox)
ks_define_len_VBoxWidget = widgets.VBox([
    widgets.Label(value='Maximum key length for the key space?'),
    ks_define_len_SliderWidget
])


# Key space allowed characters - SelectWidget
ks_allowed_chars_SelectWidget = widgets.SelectMultiple(
    options=KeySpace.PREBUILT_CHAR_LIST)

# Key space allowed characters - Label over SelectWidget (VBox)
ks_allowed_chars_VBoxWidget = widgets.VBox([
    widgets.Label(value='Choose allowable characters for the key space'),
    ks_allowed_chars_SelectWidget
])


# Key space keys can less than max key length - Checkbox
ks_smaller_keys_CheckWidget = widgets.Checkbox(
    value=False
)

# Key space keys can less than max key length - Label next to Checkbox (HBox)
ks_smaller_keys_HBoxWidget = widgets.HBox([
    widgets.Label(
        value='In key space, include all keys less than max key length?',
        # This does nothing?
        layout=widgets.Layout(text_align='right')),
    ks_smaller_keys_CheckWidget
])


# Key space "Set" button - Button
ks_set_ButtonWidget = widgets.Button(description='Set key space')

# Key space "Set" button - Button callback
ks_set_ButtonWidget.on_click(lambda b:
                                  ks_set_ButtonWidget_callback(KeySpace(
                                          ks_define_len_SliderWidget.value,
                                          ks_allowed_chars_SelectWidget.value,
                                          ks_smaller_keys_CheckWidget.value),
                                      ks_OutputWidget)
                                 )

# Key space tab layout
ks_tab_layout_VBoxWidget = widgets.VBox([
    widgets.HBox([
        ks_define_len_VBoxWidget,
        ks_allowed_chars_VBoxWidget,
        ks_set_ButtonWidget]),
    ks_smaller_keys_HBoxWidget])



# Just to double check...
# display(ks_tab_layout_VBoxWidget)
# display(ks_OutputWidget)


# Lay out the tab that allows the user to generate a couple keys from the defined key space
def keyGen_ButtonWidget_callback(keyspace, output_widget):
    with output_widget:
        if keyspace.size() <= 0:
            print("Make sure you first define the key space using the previous tab.")
        else:
            print(keyspace.generate_key(10))


keyGen_Output = widgets.Output(layout={'border': '1px solid black'})


# Generate key space keys - Button
keyGen_ButtonWidget = widgets.Button(description='Generate keys')

# Generate key space keys - Button callback
keyGen_ButtonWidget.on_click(lambda b:
                                  keyGen_ButtonWidget_callback(KeySpace(
                                          ks_define_len_SliderWidget.value,
                                          ks_allowed_chars_SelectWidget.value,
                                          ks_smaller_keys_CheckWidget.value),
                                      keyGen_Output)
                                 )


# Clear generated key space keys - Button
keyGen_clear_ButtonWidget = widgets.Button(description='Clear output')

# Clear generated key space keys - Button callback
keyGen_clear_ButtonWidget.on_click(lambda b: keyGen_Output.clear_output())


# Generated keys tab layout
keyGen_tab_layout_VBoxWidget = widgets.VBox([
    widgets.HBox([
        keyGen_ButtonWidget,
        keyGen_clear_ButtonWidget]),
    keyGen_Output
])


# Just to double check...
# display(keyGen_tab_layout_VBoxWidget)


# Lay out the tab that allows the user to check whether a provided key exists in the defined key space
def checkKey_search_ButtonWidget_callback(search_key, keyspace, output_widget):

    # As above - Take the "nice to look at" allowable characters passed to
    # this function and expand them into an equivalent "nice for Python to
    # work with" list
    # expanded_allowable_chars = expand_allowable_chars(allowable_chars)
    
    # Clear all text that exists in the 'output' widget area (the area where
    # we print send output for the "Search parameters" section).
    output_widget.clear_output()
    
    # The function 'check_search_key()' is defined further below. It does
    # the actual work of verifying whether the target key we're looking for
    # will actually exist in the defined key space.
    #
    # 'check_search_key()' will generate output that is captured by
    # 'output_widget', but is also returns '-1' if it decides 'search_key'
    # won't be found in the key space, and '1' if it believes it will be found.
    with output_widget:
        searchKeyStatus = keyspace.key_exists(search_key)

        # Exit callback function is 'check_search_key()' thinks we won't find the
        # target key in the key space. We don't need to tell the user what has
        # happened because 'check_search_key()' will have done that for us.
        if searchKeyStatus == -1:
            # A 'return' statement, used this way, bails out of the function right
            # away. So if this 'if' statement is entered, any subsequent code in
            # the function will not be executed.
            return
    
    # Lets find a key!
    output_widget.append_stdout("A valid key for your key space!")


checkKey_Output = widgets.Output(layout={'border': '1px solid black'})


# Keys to check for - Text
checkKey_list_TextWidget = widgets.Text(
    placeholder='Enter keys to check')


# Check for existence of provided keys - Button
checkKey_search_ButtonWidget = widgets.Button(description='Confirm key')

# Check for existence of provided keys - Button callback
checkKey_search_ButtonWidget.on_click(lambda b:
                                  checkKey_search_ButtonWidget_callback(
                                      checkKey_list_TextWidget.value,
                                      KeySpace(
                                          ks_define_len_SliderWidget.value,
                                          ks_allowed_chars_SelectWidget.value,
                                          ks_smaller_keys_CheckWidget.value),
                                      checkKey_Output)
                                 )


# Generated keys tab layout
checkKey_tab_layout_HBoxWidget = widgets.HBox([
    widgets.VBox([
        widgets.Label(value='What key would you like to search the key space for?'),
        checkKey_list_TextWidget,
        checkKey_search_ButtonWidget
    ]),
    checkKey_Output])


# Just to double check...
# display(checkKey_tab_layout_HBoxWidget)

def ks_display():
    # Assemble the previous layouts into a tabbed box

    keyspace_TabWidget = widgets.Tab(children = [
         ks_tab_layout_VBoxWidget,
         keyGen_tab_layout_VBoxWidget,
         checkKey_tab_layout_HBoxWidget]
    )

    keyspace_TabWidget.set_title(0, 'Define the key space')
    keyspace_TabWidget.set_title(1, 'Generate keys')
    keyspace_TabWidget.set_title(2, 'Check for a key')

    display(keyspace_TabWidget)
    print("Your defined key space:")
    display(ks_OutputWidget)


def ks_define_layout():
    return ks_tab_layout_VBoxWidget
    # display(ks_OutputWidget)
    

def ks_get_OutputWidget():
    return ks_OutputWidget

def ks_get_keyspace():
    # Return None if the key space has not been set
    if len(ks_allowed_chars_SelectWidget.value) < 1:
        return None
    else:
        return KeySpace(
            ks_define_len_SliderWidget.value,
            ks_allowed_chars_SelectWidget.value,
            ks_smaller_keys_CheckWidget.value)
