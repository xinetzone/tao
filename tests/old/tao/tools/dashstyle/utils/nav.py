from dash import html

__all__ = ['create_nav']


def create_icon_button(icon_class, icon_name, button_id=''):
    icon = html.I(f' {icon_name}', className=icon_class)
    button = html.Button(icon,
                         className='w3-button w3-padding-small',
                         type='button',
                         id=button_id)
    return button


def create_icon_label(icon_class, icon_name, htmlFor):
    icon = html.I(f' {icon_name}', className=icon_class)
    label = html.Label(icon,
                       className='w3-bar-item w3-button',
                       id=htmlFor,
                       htmlFor=htmlFor)
    return label


def create_label_li(label):
    li = html.Li(label)
    return li


def create_ul(li_list):
    ul = html.Ul(li_list,
                 className="w3-dropdown-content w3-bar-block w3-card-4")
    return ul


def create_menu(labels, button_icon_class, button_icon_name):
    li_list = [create_label_li(label) for label in labels]
    ul = create_ul(li_list)
    button = create_icon_button(button_icon_class, button_icon_name)
    return html.Section([button, ul], className='w3-dropdown-hover')


def create_nav():
    file_labels = [create_icon_label(*k) for k in [['fas fa-file', 'open file', 'open_file'],
                                                   ['fas fa-trash',
                                                       'Trash', 'trash'],
                                                   ['fas fa-window-close', 'Close', 'close']]]
    file_icon_name = 'file'
    file_icon_class = 'far fa-file'
    file_sec = create_menu(file_labels, file_icon_class, file_icon_name)

    edit_labels = [create_icon_label(*k) for k in [['fas fa-film', 'cv', 'cv'],
                                                   ['fas fa-map-marked-alt',
                                                       'radar', 'radar'],
                                                   ['fas fa-car', 'vehicle', 'vehicle']]]
    edit_icon_name = 'edit'
    edit_icon_class = 'fas fa-edit'
    edit_sec = create_menu(edit_labels, edit_icon_class, edit_icon_name)

    display_labels = [create_icon_label(*k) for k in [['fas fa-film', 'display cv', 'display_cv'],
                                                      ['fas fa-map-marked-alt',
                                                       'display radar',
                                                       'display_radar'],
                                                      ['fas fa-car', 'display vehicle', 'display_vehicle']]]
    display_icon_name = 'display'
    display_icon_class = 'fas fa-eye'
    display_sec = create_menu(
        display_labels, display_icon_class, display_icon_name)

    run_labels = [create_icon_label(*k) for k in [['fas fa-play', 'start', 'start'],
                                                  ['fas fa-stop', 'stop', 'stop']]]
    run_icon_name = 'run'
    run_icon_class = 'far fa-play-circle'
    run_sec = create_menu(run_labels, run_icon_class, run_icon_name)

    nav = html.Nav([file_sec, edit_sec, display_sec, run_sec],
                   className='w3-bar w3-bottombar w3-border-top')
    return nav
