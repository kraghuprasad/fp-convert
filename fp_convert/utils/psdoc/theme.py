"""
Following classes specify the default values for various parameters of Program
Specifications Document (PSD).
It is possible to construct and reconfigure them, before constructing the PSD
template. Then those reconfigured classes can be supplied to the constructor of
the template.
"""

# from fp_convert.utils.helpers import ObjectMix


class Config:
    """
    Following controls the document-specific configuration parameters.
    """

    toc_depth = 3  # Maximum depth required for the table of contents listing
    sec_depth = 5  # Maximum depth allowed while sectioning this document
    par_title_format = (
        r"[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}"  # noqa
    )
    par_title_spacing = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    subpar_title_format = (
        r"[hang]{\normalfont\normalsize\bfseries}{\thesubparagraph}{1em}{}"  # noqa
    )
    subpar_title_spacing = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    new_mark_text = "NEW"  # Text marking newly added nodes
    new_mark_flag = r"\faPlus"  # FontAwesome icon for new-markings
    del_mark_text = "CUT"  # Text marking nodes for removal
    del_mark_flag = r"\faCut"  # FontAwesome icon for del-markings
    timezone = "UTC"  # Timezone for all timestamps used in the document


class Geometry:
    """
    Following attributes define various geometry specific parameters of the
    page.
    """

    figure_width = r"0.6\textwidth"  # Width of the figure, in LaTeX
    header_thickness = "0.4"  # Header line thickness
    footer_thickness = "0.4"  # Footer line thickness
    left_margin = "1.25in"
    inner_margin = "1.25in"  # Applicable only in twosided mode
    right_margin = "1.25in"
    sf_outer_line_width = "1pt"  # Stop-Frame outer line-width size
    sf_round_corner_size = "3pt"  # Stop-Frame rounded corner's size
    sf_outer_left_margin = "5pt"  # Stop-Frame outer left margin width
    sf_inner_left_margin = "10pt"  # Stop-Frame inner left margin width
    sf_outer_right_margin = "5pt"  # Stop-Frame outer right margin width
    sf_inner_right_margin = "30pt"  # Stop-Frame inner right margin width
    outer_margin = "1.25in"  # Applicable only in twosided mode
    top_margin = "1.5in"
    bottom_margin = "1.5in"
    head_height = "20pt"
    par_indent = "0pt"

    # Vertical space between top logo and title-text in the title page
    tp_top_logo_vspace = "5cm"
    tp_top_logo_height = "3cm"  # Height of top logo on title page

    # Vertical space between bottom logo and title-text in the title page
    tp_bottom_logo_vspace = "7cm"
    tp_bottom_logo_height = "1.5cm"  # Height of bottom logo on title page

    l_header_image_height = "0.7cm"
    c_header_image_height = "0.5cm"
    r_header_image_height = "0.5cm"
    l_footer_image_height = "0.5cm"
    c_footer_image_height = "0.5cm"
    r_footer_image_height = "0.5cm"


class Table:
    """
    Following colors are defined for the default tables laid out in PSD.
    """

    header_text_color = "darkblue"
    header_row_color = "babyblueeyes!80"
    footer_row_color = "babyblueeyes!10"
    rowcolor_1 = "babyblueeyes!35"
    rowcolor_2 = "babyblueeyes!20"
    line_color = "cornflowerblue"


class DBSchemaTable:
    """
    Following colors are defined for the database tables laid out in PSD.
    """

    tab1_header_row_color = "spirodiscoball!20!white"
    tab1_header_line_color = "fpcblue2"
    tab1_header_text_color = "darkblue"
    tab1_body_line_color = "gray!30"
    tab2_header_row_color = "fpcblue1"
    tab2_header_line_color = "fpcblue2"
    tab2_header_text_color = "darkblue"
    tab2_rowcolor_1 = "white"
    tab2_rowcolor_2 = "tealblue!7!white"


class Colors:
    """
    Following colors are defined for styling the PSD.
    """

    header_line_color = "airforceblue"
    footer_line_color = "airforceblue"
    link_color = "celestialblue"
    url_color = "ceruleanblue"
    file_color = "magenta"
    mc_color = "{rgb}{0,0.5,0}"  # Color of margin comments
    sf_line_color = "cadmiumred"  # Stop-Frame line-color
    sf_background_color = "red!5!white"  # Stop-Frame background-color
    new_mark_color = "cobalt"  # Color of markers for newly created nodes
    del_mark_color = "red!80!gray"  # Color of markers for nodes marked for deletion
