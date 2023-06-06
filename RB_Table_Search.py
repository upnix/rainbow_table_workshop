from RainbowTables import RainbowTable
from Key_Space_Widgets import ks_get_keyspace
import ipywidgets as widgets

search_direction = 'rtl'

def bad_hash_reduce(hash_digest, salt, key_length, allowable_chars):
    new_key = str()
    i = 0
    for c in hash_digest:
        for digit_str in str(ord(c)):
            if int(digit_str) < len(allowable_chars):
                new_key += allowable_chars[int(digit_str)]
            else:
                new_key += random.choice(allowable_chars)
        if len(new_key) >= key_length:
            break
        
    return new_key[:key_length]

def ts_targetHash_callback(button, rb, str_to_find, direction, int_widget, table_widget, status_Output):

    cur_str_to_find = str_to_find
    iteration_attempt = int_widget.value
    int_widget.value += 1

    rb.html_table.add_row(list())
    
    if direction == 'rtl':
        col_loc = (len(rb.html_table.header_row)-1)-4*iteration_attempt
    else:
        col_loc = 0
        
    rb.html_table.table_content[-1][col_loc] = '<b>' + cur_str_to_find + '</b>'

    for i in range(0, iteration_attempt):
        if direction == 'rtl':
            next_val = rb.reduction_func(cur_str_to_find)
        else:
            next_val = rb.hash_func(cur_str_to_find)

        # Location of follow-up key
        col_loc += 2
        rb.html_table.table_content[-1][col_loc-1] = '=>'
        
        rb.html_table.table_content[-1][col_loc] = next_val


        rb.html_table.table_content[-1][col_loc+1] = '=>'

        if direction == 'rtl':
            cur_str_to_find = rb.hash_func(next_val)
        else:
            cur_str_to_find = rb.reduction_func(next_val)

        # Location of subsequent digest
        col_loc += 2
        
        rb.html_table.table_content[-1][col_loc] = cur_str_to_find


    if direction == 'ltr':
        rb.html_table.table_content[-1][col_loc+1] = '=>'
        rb.html_table.table_content[-1][col_loc+2] = rb.hash_func(cur_str_to_find)
    key_found = False
    #if direction == 'rtl':
    for i in range(0, len(rb.table)):
        if cur_str_to_find in rb.table[i][-1]:
            rb.html_table.highlight([i, len(rb.html_table.header_row)-1])
            rb.html_table.highlight([len(rb.html_table.table_content)-1, len(rb.html_table.header_row)-1])
            key_found = i+1
    # cur_str_to_find = target_digest
    table_widget.value = rb.html_table.generate_table()
    if key_found:
        #button.disabled = True
        status_Output.append_stdout(f'A matching hash digest has been found in the last column of row {key_found}.\n{iteration_attempt} iterations of reducing a hash digest to a key belonging to the key space, then hashing the result were necessary to find the match.')
        return
    #else:
    #    table_widget.value = rb.html_table.generate_table()
    #    status_Output.append_stdout("Haven't sorted this out yet.")


def ts_table_blackout_callback(button, num_rows, html_table, table_widget):

    # Bottom-right coordinates of table
    row = num_rows - 1
    col = len(html_table.header_row)-3

    if button.description == 'Turn on':
        button.description = 'Turn off'
        html_table.blackout_range([0,1], [row, col])
    else:
        button.description = 'Turn on'
        html_table.clear_tags([0,1], [row, col])

    table_widget.value = rb.html_table.generate_table()


def ts_reset_callback(rb, text_widget, int_widget, blackout_button, search_button, table_widget, status_Output):
    rb.display_table(table_widget, 10)
    text_widget.value = ''
    int_widget.value = 0
    blackout_button.description='Turn on'
    search_button.disabled = False
    status_Output.clear_output()
    

def ts_direction_callback(radio_widget, text_widget, int_widget):
    global search_direction
    if radio_widget.new == 'Start from key (Left-to-right)':
        search_direction = 'ltr'
        text_widget.placeholder='Plain-text key'
    else:
        search_direction = 'rtl'
        text_widget.placeholder='Hash digest to find'
    
    int_widget.value = 0

# Make the Rainbow table
rb = RainbowTable(ks_get_keyspace(), 5, 10)

table_widget = widgets.HTML()
ts_status_Output = widgets.Output(layout={'border': '1px solid black'})



ts_col_BoundedInt = widgets.BoundedIntText(value = 0, disabled=True)
ts_col_BoundedInt.layout.width = '100px'

ts_target_Text = widgets.Text(placeholder='Hash digest to find')

ts_direction_Radio = widgets.RadioButtons(
    options=['Start from key (Left-to-right)', 'Start from hash (right-to-left)'],
    value='Start from hash (right-to-left)')

ts_direction_Radio.observe(lambda b: ts_direction_callback(b, ts_target_Text, ts_col_BoundedInt), names='value')



ts_targetHash_Button = widgets.Button(description='Search')
ts_targetHash_Button.on_click(lambda b: ts_targetHash_callback(
    b,
    rb,
    ts_target_Text.value,
    search_direction,
    ts_col_BoundedInt,
    table_widget,
    ts_status_Output))


ts_table_blackout_Button = widgets.Button(description='Turn on')
ts_table_blackout_Button.on_click(lambda b: ts_table_blackout_callback(b, rb.table_rows, rb.html_table, table_widget))


ts_reset_Button = widgets.Button(description='Reset')
ts_reset_Button.on_click(lambda b: ts_reset_callback(
    rb, ts_target_Text, ts_col_BoundedInt, ts_table_blackout_Button, ts_targetHash_Button, table_widget, ts_status_Output))


def display_table_search():
    table_layout = widgets.Layout(display = 'flex', border='1px solid black', align_items='center')
    display(widgets.HBox([
        widgets.VBox([widgets.Label(value='Key/digest to start your search from', style = dict(text_decoration='underline')),ts_target_Text], layout=table_layout),
        widgets.VBox([widgets.Label(value='Reduce/Hash iterations', style = dict(text_decoration='underline')), ts_col_BoundedInt], layout=table_layout),
        widgets.VBox([
            widgets.Label(value='Blackout center of table', style = dict(text_decoration='underline')),
            ts_table_blackout_Button], layout = table_layout),
        widgets.VBox([ts_targetHash_Button, ts_reset_Button], layout = table_layout)
        ]),
        ts_direction_Radio)

def display_rb_table():
    display(widgets.VBox([
        table_widget,
        ts_status_Output]))
    
    # Display the Rainbow table
    rb.display_table(table_widget, 10)


def display_bad_reduction_table():
    bad_rb = RainbowTable(ks_get_keyspace(), 5, 10, bad_hash_reduce)
    bad_table_widget = widgets.HTML()
    bad_rb.display_table(bad_table_widget, 10)
    key_digest_dup = dict()
    row_count = 0
    for row in bad_rb.table:
        chain_pair = 0
        for key, _ in row:
            if key in key_digest_dup:
                bad_rb.html_table.highlight([row_count, 4*chain_pair])
                i, k = key_digest_dup[key]
                bad_rb.html_table.highlight([i,4*k])
            else:
                key_digest_dup[key] = (row_count,chain_pair)
            chain_pair += 1
        row_count += 1
    bad_table_widget.value = bad_rb.html_table.generate_table()
    
    display(bad_table_widget)