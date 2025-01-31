import random
import functools
from IPython.display import display, clear_output
from ipywidgets import Button, Dropdown, HTML, HBox, VBox, IntSlider, FloatSlider, Textarea, Output, Layout

def annotate(examples,
             options=None,
             shuffle=False,
             include_skip=True,
             display_fn=display):
    """
    Build an interactive widget for annotating a list of input examples.

    Parameters
    ----------
    examples: list(any), list of items to annotate
    options: list(any) or tuple(start, end, [step]) or None
             if list: list of labels for binary classification task (Dropdown or Buttons)
             if tuple: range for regression task (IntSlider or FloatSlider)
             if None: arbitrary text input (TextArea)
    shuffle: bool, shuffle the examples before annotating
    include_skip: bool, include option to skip example while annotating
    display_fn: func, function for displaying an example to the user

    Returns
    -------
    annotations : list of tuples, list of annotated examples (example, label)
    """
    examples = list(examples)
    if shuffle:
        random.shuffle(examples)

    def set_label_text():
        non_local["count_label"].value = '{} examples annotated, {} examples left'.format(
            len(annotations), len(examples) - non_local["current_index"]
        )

    def show_next():
        non_local["current_index"] += 1
        set_label_text()
        if non_local["current_index"] >= len(examples):
            for btn in buttons:
                btn.disabled = True
            print('Annotation done.')
            return
        with out:
            clear_output(wait=True)
            display_fn(examples[non_local["current_index"]])

    def add_annotation(annotation):
        annotations.append((examples[non_local["current_index"]], annotation))
        show_next()

    def skip(btn):
        show_next()

    def create_expanded_button(description, button_style):
        return Button(description=description, button_style=button_style, layout=Layout(height='auto', width='auto'))

    annotations = []
    non_local = {"current_index" : -1, "count_label" : HTML()}
    set_label_text()
    display(non_local["count_label"])

    if type(options) == list:
        task_type = 'classification'
    elif type(options) == tuple and len(options) in [2, 3]:
        task_type = 'regression'
    elif options is None:
        task_type = 'captioning'
    else:
        raise Exception('Invalid options')

    buttons = []
    
    if task_type == 'classification':
        # use_dropdown = len(options) > 5
        # hardcoding dropdown to false
        use_dropdown = False

        if use_dropdown:
            dd = Dropdown(options=options)
            display(dd)
            btn = create_expanded_button('submit', 'success')
            def on_click(btn):
                add_annotation(dd.value)
            btn.on_click(on_click)
            buttons.append(btn)
        
        else:
            for label in options:
                btn = create_expanded_button(label, 'info')
                def on_click(label, btn):
                    add_annotation(label)
                btn.on_click(functools.partial(on_click, label))
                buttons.append(btn)

    elif task_type == 'regression':
        target_type = type(options[0])
        if target_type == int:
            cls = IntSlider
        else:
            cls = FloatSlider
        if len(options) == 2:
            min_val, max_val = options
            slider = cls(min=min_val, max=max_val)
        else:
            min_val, max_val, step_val = options
            slider = cls(min=min_val, max=max_val, step=step_val)
        display(slider)
        btn = Button(description='submit')
        def on_click(btn):
            add_annotation(slider.value)
        btn.on_click(on_click)
        buttons.append(btn)

    else:
        ta = Textarea()
        display(ta)
        btn = Button(description='submit')
        def on_click(btn):
            add_annotation(ta.value)
        btn.on_click(on_click)
        buttons.append(btn)

    if include_skip:
        btn = Button(description='skip', button_style='warning')
        btn.on_click(skip)
        buttons.append(btn)

    out = Output()
    display(out)

    box = VBox(buttons)
    display(box)

    show_next()

    return annotations
