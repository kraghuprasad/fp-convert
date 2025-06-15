version: 0.2.0

# fp-convert 

If you use mindmaps to capture and manage information, but others working with you find them quite cumbersome to read and understand, then fp-convert is for you. It converts a [Freeplane](https://docs.freeplane.org/) mindmap to print-quality PDF documents. At present it converts a mindmap to a project specifications document. The same template can be used to build any knowledge-base and print it out as a beautiful PDF document. It uses LaTeX/pdflatex text processing system to create the PDF file.

Following image summarizes what fp-convert can do if it is provided with a suitably prepared freeplane mindmap.
![fp-convert [options] mindmap-file pdfyy-file](docs/examples/blooper-specs/images/fp-convert-summary-image.png)

## Why it matters?

Once upon a time, people used to understand that there existed a separation between contents of a document and its representation. But that has mostly been blurred for majority of people today who jump onto any available writing or presentation tool to capture and maintain information. Until we understand this separation, it would not be possible to select the most suitable tool for any knowledge management needs. While dealing with projects - and specifically software projects - we regularly find people capturing and maintaining functional and program specifications in Word docs, Excel spreadsheets and (Horror!!!) Powerpoint presentations. Those who have used such tools to write project specifications also know the inherent challenges in maintaining them over a long period of time, sometimes stretching over decades. Some of the common problems associated with these kinds of tools are listed below.

- It takes a lot of efforts to focus on certain sections of the specifications document while modifying it. The specifications are mostly inter-related, and changing one section may have its own side effects on other sections of the document, which may be tens of pages away from the current one. Then it becomes a repetitive jumping between various pages, sections, tables, and images while modifying a document.
- Navigating through a large document, spreadsheet or presentation itself makes the whole process quite tedious. For example while looking at a particular response obtained from an API call, one may want to know the relevance of certain data point which is part of the response. Those details might have been stored somewhere in the functional specifications section in the same document. Linking those sections, and then maintaining them properly throughout the project execution and maintenance period may not be simple. Due to large spread of the content, people may find it difficult to separate and focus only on the affected sections (this is easily handled in mindmaps, by the way) of the document.
- While writing the content of the document, using different versions of the same tool on different machines may result in changes in the document-styles. Such changes are visible mostly in the fonts and font-styles. This creates an unwanted distraction or jarring effect on the reader who wants to focus on the content rather than on its presentation.
- If multiple people are formatting a document over a long period of time, their styles of writing as well as formatting starts changing. In large documents which have passed through multiple hands over the years, you may find that some section of the document being formatted in fixed sized fonts, while the similar content being formatted with variable sized fonts in other sections of the same document. The fonts and formatting are considered good if they are used to convery required information clearly to the reader of the document. Otherwise they just add only to the clutter. A badly formatted document quickly becomes unreadable, and people would lose interest in maintaining it over a period of time. Unmaintained documentation is as good as no documentation.
- Except PDF, HTML, or Markdown text, there exists no standard document formats which render properly on multiple document-viewers running on different operating systems. For example, documents or presentations created using Microsoft Office on Windows do not render properly in Libre Office running on Linux or Unix-like systems, even if though such file formats are stated to be supported by it. This itself should be sufficient enough to discard those tools for knowledge management purpose for any project. Forcing everyone to opt for a particular OS or program to access a particular document helps only to prop-up the bottomlines of respective companies which create those OS and documentation tools with all kinds of vendor-lock-ins. It does not serve the users for whom those documents were created at the first place.

To solve these problems we can opt for TeX/LaTeX as our preferred documentation tool. It is fully open source and it also allows us to maintain the separation between content and style for any document. It is possible to convert a TeX based document to corresponding PS or PDF files, which are known as portable file formats. They are guaranteed to render correctly everywhere and there exists many open as well as closed sourced tools to view them on any OS. Modern PDF documents support hyperlinks too which are essential for cross referencing within sections of a document.

While writing the document, the author can decide to chose the right format to display a particular content. For example, the same content can be formatted in a tabular form (in spread-sheets), in paragraphs of text (in word docs), flowcharts (using Visio or LibreDraw) or in any other suitable form. This is the prerogative of the producer (author) to decide how certain content should be rendered to convey the required information to the consumer (reader) of the document. This requires good understanding on the producer's part on what to show in which format. We find that the lack of such understanding, along with misuse of existing text or data formatting tools have actually blurred the line of distinction between content and its presentation. We regularly find badly formatted documents where even the section-headers are not suitably defined. Many consider that the headers of a section means just few phrases formatted in bold-text. This kind of formatting makes it impossible to auto-generate the table of contents of a large document along with its section-headers and page numbers. If we define the structure of the documents correctly, then existing text processing tools like TeX/LaTeX, Microsoft Word, Libreoffice Writer; or cloud based text editors like Google Docs, O365 Word etc. would be able to auto-generate the table of contents of our documents for us whose sections could be accurately hyperlinked to their respective page numbers.

TeX/LaTeX is an advanced text processing tool. By using its various standard document templates prudently, we can ensure that the resultant documents would be following all pertinent typesetting rules. Since many people are not familiar with the rules of document typesetting, it is always better to leave that job to a suitable tool like TeX. Proper typesetting is mandatory for a document to make its content easily accessible to the readers of it. The fp-convert program uses TeX/LaTeX to typeset the documents generated from [Freeplane](https://docs.freeplane.org/) mindmap.

Though it is easy to generate any kind of document using WYSIWYG text editors, there are scenarios where the end results may not turn out to be useful for the consumers of those documents. One such scenario is writing functional or implementation specifications of a project, for which people resort to Word docs, excel sheets or Powerpoint presentations. Each of them have their own set of problems to capture and manage the knowledge involved in a project. Another such example is creation of a relational database schema for a database designed for an enterprise application. It is important to ensure that the DB schema is made accessible to the developers in an easily accessible manner. A spreadsheet or a presentation slide may not be the most suitable format to capture and render such information to the people.

## Documentation Tools for System Architects

Any kind of designing can be a non-linear activity. Hence, it is required to add or remove contents in design specifications in a non-linear manner. While doing so, it is important to maintain required cross-references between its sections correctly. This is required not only during the design and development periods of any system, it might be needed to be done for every change-requests received from the client after the application has gone in production. The system specification documents may need various kinds of diagrams, tables, lists of entities etc. along with descriptive text to define the underlying functional or implementation details. Though we can create such content in plain text using any WYSIWYG text processor, soon it becomes tedious to maintain it for a long period of time. Sometimes such documents are to be updated and maintained for decades. Even using TeX/LaTeX for it would make that work quite tedious and cumbersome. Just to create cross references among sections, tables, lists etc. in LaTeX, one needs to write large amount of text to define labels and hyperlinks. Besides that, one needs to know basic concepts of TeX quite well to debug issues which may crop up during the compilation of the document.

The solution to this problem lies in selecting two separate tools for writing and reading. One can use a mindmap to document the knowledge, where it allows the author to focus on specific nodes while writing. By rendering that mindmap into a properly cross-referenced PDF document, one can avoid almost all kinds problems listed above. That's what fp-convert does. It converts mindmaps created by Freeplane into correctly formatted documents in PDF format.

For many decades now, the mindmaps have turned out to be quite useful to brainstorm ideas, and to design and document solutions for various problems. If one writes the project specifications in a mindmap, while following certain conventions, the fp-convert can generate properly typeset document from it. The resultant document would be portable across all major operating systems. Also the text (XML) based mindmap created by Freeplane can be easily stored in any code and configuration repository like git, subversion, VSS etc. along with other project assets. This ensures single source of knowledge for the whole project under strict version-controls.

## License

This application is released under GNU Public License (v3). You are free to use it for commercial as well as non-commercial purposes, as long as your work remains compliant to the underlying licensing terms of GPL(v3).

## Installation

fp-convert is standing on the shoulders of giants like Python and TeX/LaTeX which doesn't need any introductions. But two critical components without which this endeavor would not have been possible are [PyLaTeX](https://github.com/JelteF/PyLaTeX) and [freeplane-python-io](https://github.com/nnako/freeplane-python-io) (thanks nnako for all those timely help :).

This program requires a recent version of Python3 to work. You may install Python stack system-wide or to a specific vertual environment. For system-wide installation from Python package repository, please execute the following command on the console.

```bash
pip install fp-convert
```

It will download all Python based dependencies automatically. But you also need a fully functional TeX/LaTeX environment installed on your machine to use this tool. It is freely available for all major operating systems. Please refer your OS manual or user communities on the Internet to know how to install TeX/LaTeX on your favorite operating system.

On Linux based machines you may find that following tex-packages get installed as part of full TeX installation.

- texlive-base
- texlive-latex-base
- texlive-latex-recommended
- texlive-fonts-recommended
- texlive-fonts-extra
- texlive-latex-extra
- texlive-pictures
- texlive-science
- texlive-latex-extra

If full texlive package is not available on your machine due to disk-space crunch, or due to some other reasons; then at least a TeX/LaTeX environment with following packages must be made available for fp-convert to work properly:

- amssymb
- enumitem
- fontawesome5
- fontenc
- geometry
- hyperref
- longtable
- makecell
- marginnote
- mdframed
- multirow
- placeins
- ragged2e
- tabularx
- tcolorbox
- titlesec
- utopia
- xcolor
- xspace

You should also install all those additional TeX packages on which the command-line-options to fp-convert depends on. For example, you may need to install additional font-packages, if you are not satisfied with the default `lmodern` or `roboto` font-family for your documents. In such case, you may need to install additional fonts on your system.

If you are planning to generate UML usecase diagrams too, then you must install
[PlantUML](https://plantuml.com/) on the system running fp-convert. Please be
warned that adding node-level attributes required to generate UML diagram may
quickly become a boring chore while creating your mindmaps. To ease that pain,
[i-plasm](https://github.com/i-plasm) and [euu2021](https://github.com/euu2021) have collaborated to create an excellent groovy script named [Dynamic Types Creator](https://github.com/i-plasm/freeplane-types-creator) which should be placed in the scripts folder of your [Freeplane](https://docs.freeplane.org/) installation folder. You should map a keyboard shortcut -- I use "Alt+t" -- to run Dynamic Type Creator script. This can be configured from within the freeplan program by goint to "Tools -> Assign hot key", selecting applicable script, and then pressing those keybord shortcuts to register it in Freeplane. Please refer the documentation of [Freeplane Hot Keys](https://docs.freeplane.org/user-documentation/hot-keys-and-beyond.html) for further information on instlalation, configuration and enabling keyboard shortcuts for any script based plugins.

You must download [Blooper_Specifications.mm](https://github.com/kraghuprasad/fp-convert/blob/main/docs/examples/blooper-specs/Blooper_Specifications.mm), open it in freeplane, copy the "Templates" node of it, and paste the same into the root node of your own mindmap to acquire all pertinent templates used by fp-convert. You can leave its child-nodes in collapsed state in your mindmap, and it won't get rendered in the output of fp-convert either. You may add additional node-templates under it too for your own use. The details of syntax and semantics applicable to define such templates can be found in this [discussion thread](https://github.com/freeplane/freeplane/discussions/2365#discussioncomment-12807085).

## Operating Systems

Please note that this program was built and tested on a Manjaro Desktop which is based on Arch Linux. It is expected that it will work without any issues on other Linux distributions like Debian, Ubuntu, Fedora and all other distros built using them. In fact it should work with any unix-like system like FreeBSD, OpenBSD, NetBSD, DragonFlyBSD, etc. too provided the software dependencies of fp-convert are met. It may also work on Windows and MacOS, provided all required TeX and other Python packages are installed on in. Your mileage may vary though. We would like to hear the experience of users who could get it working on BSD, Windows and Mac.

## Usage

Executing `fp-convert -h` results in its help-text getting displayed.

---

```txt
usage: fp-convert [-h] [-t <template-name>] [-k]
                  [-f <font-family-name:font-family-options>]
                  [-c <config-file-path>] [-d] [-g <config-file-path>]
                  [mindmap_file] [output_file]

Program to convert a Freeplane mindmap's content into a print-quality PDF
document. If only relative file-paths are used to define the resources (like
images) used in the mindmap, then run this program from the folder in which
the mindmap file is situated. In case absolute paths are used in the resource-
paths within the mindmap, then this program can be executed from anywhere, as
long as appropriate input and output file-paths are provided to it.
Appropriate options are provided using which the TeX file generated by this
program can be preserved. Then it can be used to inspect the structure of the
mindmap before conversion to PDF. The generated TeX file can be compiled using
pdflatex in any folder on the same machine on which fp-convert was executed to
generate it.

positional arguments:
  mindmap_file          input freeplane mindmap file-path
  output_file           output PDF file-path

options:
  -h, --help            show this help message and exit
  -t <template-name>, --template <template-name>
                        template to be used for converting to TeX/LaTeX file
  -k, --keep-tex        keep intermediate TeX/LaTeX file
  -f <font-family-name:font-family-options>, --font-family <font-family-name:font-family-options>
                        font-family to be used while building the PDF file
                        Correct LaTeX options are required to be passed-on
                        while supplying this parameter. Incorrect options, if
                        supplied, would result in TeX-compilation failures.
                        The option -k can be used to debug such issues by
                        preserving the resultant TeX file for further
                        inspection. Examples: roboto (The Roboto family of
                        fonts to be used), roboto:sfdefault (The Roboto family
                        along with LaTeX option sfdefault),
                        roboto:sfdefault:scaled=1.1 (The Roboto family along
                        with LaTeX options sfdefault and scaled=1.1 which are
                        applicable on this font family), roboto:scaled=1.1
                        (The Roboto family of fonts scaled to 1.1), etc. You
                        need to ensure that invalid options for the chosen
                        font-family do not get supplied here.
  -c <config-file-path>, --config <config-file-path>
                        path to the YAML file with pertinent configuration
                        parameters required for converting a mindmap to PDF
                        document
  -d, --debug           preserve all intermediate files for debugging purpose
  -g <config-file-path>, --generate-config <config-file-path>
                        generates a sample configuration file of YAML type
                        which contains all pertinent configuration parameters
                        with their default values
```

---

## Features of fp-convert

fp-convert is a command-line tool written in Python which uses fp_convert module to carry out its work. The same module can be invoked from other Python programs too, to generate required PDF documents. At present it is designed to generate project specifications document for any software or IT based projects. Support for other kinds of documents would be added in future, based on the demand from the community. By the way, it should not be presumed that the document generated by fp-convert would not be useful for capturing other knowledge-items. Internally fp-convert uses LaTeX base document class `article'. Hence you can use fp-convert to generate any kind of document which can be built using that document class, as long as you follow certain conventions while creating your mindmap. The details of those conventions are given in some of the sections below.

### Print-Quality PDF Generation

fp-convert can generate PDF files using TeX/LaTeX text processing system. It creates beautiful, and compact documents which follow almost all typographic conventions followed in a standard TeX based document template.

### Metadata of Document

The document's content is kept separate from the standard meta-data like page-geometry, logo-images and their dimensions, colors of various artifacts etc. All page-layout and styling related metadata is managed via special classes like Config, Colors, Geometry, Theme etc. Those values can either be supplied programmatically - if required - or they can be fetched from a suitable configuration file while processing the document.

On the other hand, the document specific metadata which is not pertaining to the layout and styling of the document can be stored as note-text in the root node of the mindmap. They are stored in key-value format. This is fetched and processed automatically by fp-convert and rendered in the resultant PDF file at appropriate places. Except root-node of the mindmap, all other nodes should hold the contents of the document, based on which the PDF file is to be generated.

Following is a sample metadata text-block stored as note-text of root node of the sample mindmap shared with this application. The descriptions given in parentheses against each value is for information purpose only, and they should not be included in the mindmap. You may modify any of the values in your mindmap, and they would be reflected in the resultant PDF file.

---

```text
Version: 1.0  (document-version to be included on the title page)
Title: Project Specifications of Blooper App (document title)
Date: 21 January, 2025 (document-date to be printed on title page)
Author: Whoopie Bard $<$whoopie@clueless.dev$>$ (author-name with email)
Client: Blooper Inc. (client for whom project is being executed)
Vendor: Clueless Developers' Consortium (vender who is executing the project)
Trackchange_Section: Track Changes (needs to prepare track-change-list and render it in a section as named here)
TP_Top_Logo: images/tp_top_logo.pdf (top-logo image path for title page)
TP_Bottom_Logo: images/tp_bottom_logo.pdf (bottom-logo image path for title page)
L_Header_Text: Blooper Inc. (page header text for top left if image is not supplied)
L_Header_Logo: images/page_top_left_image.pdf (page header image for top left if text is not supplied)
C_Header_Text: Project Specifications of Blooper App (page header text at top center if image is not supplied for it)
C_Header_Logo: images/page_top_center_image.pdf (page header image at top center if text is not supplied for it)
R_Header_Text: Non-Confidential (page header text at top right if image is not supplied for it)
R_Header_Logo: images/page_top_right_image.pdf (page header image for top right if text is not supplied)
L_Footer_Text: created by fp-convert (page header text for bottom left if image is not supplied)
L_Footer_Logo: images/page_bottom_left_image.pdf (page header image for bottom left if text is not supplied)
C_Footer_Text: Clueless Developers' Consortium (page header text at bottom center if image is not supplied for it)
C_Footer_Logo: images/page_bottom_center_image.pdf (page header image at bottom center if text is not supplied for it)
R_Footer_Text: \small{Page \thepage\- of \pageref*{LastPage}} (page header text for bottom right if image is not supplied)
R_Footer_Logo: images/page_bottom_right_image.pdf (page header image for bottom right if text is not supplied)
Timezone: Asia/Kolkata (timezone - default is UTC - to be used while calculating timestamps, if any)
```

---

The page number format shown above for right-footer-text is using the LaTeX macros \thepage and \pageref\*{LastPage}. It prints the text "Page X of Y" on every page, where X is the current page-number, and Y is the total number of pages in the document. You may use the value "\small{\thepage} if you want only the current page-number to be printed on every page.

The credit text "Prepared using [fp-convert](https://github.com/kraghuprasad/fp-convert)" would be automatically included in the footer of every page by default. If you do not want that, then you need to supply some text (or image) for all the three footer blocks, namely left (L_Footer\_\*), center (C_Footer\_\*), and right (R_Footer\_\*) as shown in the example given above. If you want certain blocks to be kept empty, but do not want it to be auto-filled using the credit text mentioned above, then please ensure that all the keys used for defining footer-texts (\*\_Footer_Text) are either supplied with some valid values or with %%; provided no images are defined for those sections either. For example, if there are no images supplied for left section of the footer, and no text is supplied for it either, then the credit text would be automatically included there. But if you supply %% as value for L_Footer_Text, then that section would be left empty by not including credit text there. Please note that this trick is possible only with keys used for specifying the text parts of the footer. If you are using any keys meant for specifying the logo (image) paths, then they must be supplied with proper image-paths, i.e. You can not put %% as values for any of them.

The geometry, colors etc. can be modified too, but using a different configuration mechanism. Either you create respective classes (Config, Geometry, Colors, Theme, etc.) with required parameters or use a YAML based configuration file to define them which can be supplied with command-line option -c while invoking fp-convert. The details of configuration file is given in the following section.

## Control Rendering Parameters

Various document-parameters can be controlled using a configuration file, which can be supplied using -c option on command-line. A sample configuration can be generated using the -g command-line option too. Following is the content of a sample configuration file which can be used while generating the PDF from a mindmap. The details of each parameter is provided as an in-line comment on the same line.

---

```yaml
# Configuration parameters of fp-convert. You may modify it as per your
# requirements.
config:
  toc_depth: "3" # Maximum depth allowed in table of contents listing
  sec_depth: "5" # Maximum depth allowed in sectioning of the document

# Document-geometry and structural parameters
geometry:
  sf_outer_line_width: "1pt" # Stop-Frame outer line-width size (with unit)
  sf_round_corner_size: "3pt" # Stop-Frame rounded corner's size (with unit)
  sf_outer_left_margin: "5pt" # Stop-Frame outer left margin width (with unit)
  sf_inner_left_margin: "10pt" # Stop-Frame inner left margin width (with unit)
  sf_outer_right_margin: "5pt" # Stop-Frame outer right margin width (with unit)
  sf_inner_right_margin: "30pt" # Stop-Frame inner right margin width (with unit)
  header_thickness: "0.4" # Header line thickness
  footer_thickness: "0.4" # Footer line thickness
  figure_width: "0.6" # Figure-with for all figures as a factor of text-width
  left_margin: "1.25in" # Left margin (with unit)
  inner_margin: "1.25in" # Inner margin (with unit)
  right_margin: "1.25in" # Right margin (with unit)
  outer_margin: "1.25in" # Outer margin (with unit)
  top_margin: "1.5in" # Top margin (with unit)
  bottom_margin: "1.5in" # Bottom margin (with unit)
  head_height: "20pt" # Head height (with unit)
  par_indent: "0pt" # Paragraph indentation (with unit)
  tp_top_logo_vspace: "5cm" # Vertical space between title page's top logo and title text
  tp_top_logo_height: "3cm" # Height of top logo on title page
  tp_bottom_logo_vspace: "7cm" # Vertical space between title pages' text and bottom logo
  tp_bottom_logo_height: "1.5cm" # Height of bottom logo on title page
  l_header_image_height: "0.7cm" # Left header image height in all pages (with unit)
  c_header_image_height: "0.5cm" # Center header image height in all pages (with unit)
  r_header_image_height: "0.5cm" # Right header image height in all pages (with unit)
  l_footer_image_height: "0.5cm" # Left footer image height in all pages (with unit)
  c_footer_image_height: "0.5cm" # Center footer image height in all pages (with unit)
  r_footer_image_height: "0.5cm" # Right footer image height in all pages (with unit)

# Parameters specific to tables used in the general sections of the document
table:
  footer_row_color: "babyblueeyes!10" # Footer row color
  header_row_color: "babyblueeyes!60" # Header row color
  header_text_color: "darkblue" # Header text color
  rowcolor_1: "babyblueeyes!30" # Row color 1 of alternate row colors
  rowcolor_2: "babyblueeyes!10" # Row color 2 of alternate row colors
  line_color: "cornflowerblue" # Color of lines shown in table

# Parameters specific to tables describing database schema
dbtable:
  tab1_header_row_color: "spirodiscoball!20!white" # Header row color for table 1
  tab1_header_line_color: "fpcblue2" # Header line color for table 1
  tab1_header_text_color: "darkblue" # Header text color for table 1
  tab1_body_line_color: "gray!30" # Body line color for table 1
  tab2_header_row_color: "fpcblue1" # Header row color for table 2
  tab2_header_line_color: "fpcblue2" # Header line color for table 2
  tab2_header_text_color: "darkblue" # Header text color for table 2
  tab2_rowcolor_1: "white" # Row color 1 of alternate row colors for table 2
  tab2_rowcolor_2: "tealblue!7!white" # Row color 2 of alternate row colors for table 2

# Color specific parameters
colors:
  header_line_color: "airforceblue" # Color of header line of the document
  footer_line_color: "airforceblue" # Color of footer line of the document
  link_color: "celestialblue" # Color of hyperlinks in the document
  url_color: "ceruleanblue" # Color of URLs used in the document
  file_color: "magenta" # Color of file-links used in the document
  mc_color: "{rgb}{0,0.5,0}" # Color of margin comment-links in the document
  sf_line_color: "cadmiumred" # Color of the boundary lines of the Stop-Frame
  sf_background_color: y # Background color of the Stop-Frame
  new_mark_color: "cobalt" # Color of new-markers used for newly added nodes
  del_mark_color: "red!81!gray" # Color of trash-markers for nodes marked for deletion
```

---

The colors used in this configuration file can be modified if required. The list of color-names allowed to be used with fp-convert are available [here](https://kraghuprasad.github.io/fp-convert/docs/colors.html). No other color-names can be used with fp-convert, unless you resort to directly modify the generated LaTeX file and compile it yourself to PDF using a tool like pdflatex. One or more of these colors can be mixed with other colors. For example "red!25!white" can be used to get a lighter shade of red by mixing it with white. The color mixing scheme used is taken from LaTeX package xcolor. If you want to learn more about xcolor and how it can be used in LaTeX documents, then you may read [this](https://ctan.math.washington.edu/tex-archive/macros/latex/contrib/xcolor/xcolor.pdf).

### Sections, Subsections, and More

Except root node, all following nodes in a mindmap are treated as sections, their subsections, their subsubsections and more. You can attain maximum depth of 5 in this manner. The node's text is treated as header of respective sections, and the note-text in each of them are rendered as section-content. Every line-break in the note-text is taken as the start of a new paragraph in respective section. If a node is to be treated in a different way, it should be annotated with a suitable icon representing how to render it. Details of such icons are given in the following sections.

### Unordered Lists

If a node is annotated with list icon (![list icon](docs/examples/blooper-specs/images/list.png)), a nested bullet-list (generated by LaTeX's \itemize) is created using its children and their respective children. The depth of list can be up to 3. If the content of any items in a list is to be shown in bold case font, then end it with a colon(:). If the same content contains a colon(:) somewhere in the middle of the text, then LHS of colon is rendered in bold case font, and the RHS in normal case.

### Ordered Lists

If a node is annotated with list icon (![list icon](docs/examples/blooper-specs/images/list.png)) as well as input numbers icon (![input numbers icon](docs/examples/blooper-specs/images/numbers.png)), then the list created from the contents of the direct children of that node would be an ordered list. The depth of the list is not dependent on the type of the list. Overall the total depth can not be more than 3, irrespective of whichever types of lists are mixed and matched. Also annotating a node without list icon but with input numbers icon would not generate an ordered list unless at least one of the parent-node between that node and the root node is annotated with the list icon. It means, starting an ordered list with a node annotated only with the input numbers icon would not be possible. Please refer the sample mindmap provided with fp-convert to know how such lists work.

The convention for rendering text in bold case font in any list-item in the ordered list is same, as explained in the previous section describing about unordered lists.

### Tabular Views

There is support for two kinds of tables. First one is for generic table, mostly containing columns with textual content. The second is the number table where most of the columns are expected to contain numerical values, and sums of their column-values too could be required.

#### Generic Table

By annotating any node with generic icon (![generic icon](docs/examples/blooper-specs/images/table.png)), a tabular view can be built. The first level of children after that node would be rendered as first column of respective rows in that table. The second level onwards the nodes would contain the column header and content for second column onwards. Each such row should contain the text in X:Y format, where X would be the column header, and Y would be the column-value. Check the sample mindmap and the resultant PDF file to know how the contents are placed and rendered.

#### Number Table

By annotating any node with generic icon (![generic icon](docs/examples/blooper-specs/images/table.png)) together with abacus icon (![abacus icon](docs/examples/blooper-specs/images/abacus.png)) a number table can be built. Following images show the kind of nodes required to build a number table and the resultant table rendered in PDF document.

![Node of Mindmap to create Number Table](docs/examples/blooper-specs/images/number_table_mm.png)
![Number Table in PDF](docs/examples/blooper-specs/images/number_table_pdf.png)

Following conventions are applicable while building a number table.

- First child of the node representing the number table must be "\|headers\|".
- This node can contain a note-text of the form "key: value". It is used to capture additional text required to be rendered in the number table. At present only key "Column1" is useful as the value supplied to it would be used as the header-text of the first column of the number table.
- The children of this node consists of the header-text to be rendered in the number table.
- If any of these child nodes are annotated with plus sign icon (![plus sign icon](docs/examples/blooper-specs/images/plus.png)), the numerical values supplied in that particular column would be summed up and displayed in the last row (Total) of the same table. The content of such columns are aligned right in the table-cell.
- If any of these child nodes are annotated with AB button icon (![AB button icon](docs/examples/blooper-specs/images/ab.png)), then column corresponding to that header is expected to contain textual data instead of numerical ones. The text in those columns are aliged left in the table-cell. The content of rest of the columns, excluding the first one, is always aligned right in the table-cells.
- The second child onwards (except \|headers\|), the row-data is supplied. The direct child contains the text to be shown aligned left in the first column of each row.
- The children of each such node contains the data to be displayed in the remaining cells of the same row. Those contents are rendered right or left aligned, based on the annotations used in the corresponding headers defined in the first node \|headers\|.

### JSON/XML/HTML/Verbatim/Code Blocks

By annotating any node with JSON icon (![json icon](docs/examples/blooper-specs/images/json.png)), a verbatim block can be created from its content using LaTeX's verbatim environment. Please note that the whole node's content would be rendered in verbatim mode. This kind of rendering is suitable to display HTML, XML, JSON, as well as software code.

### Images

If an image is to be rendered in a particular section or subsection, then node corresponding to that section should be annotated with image icon (![image icon](docs/examples/blooper-specs/images/image.png)). The raster image formats like JPEG and PNG are supported. If you want to use vector graphics, then attach SVG based images to the node. They would be auto-converted to PDF and then used in the resultant PDF document. By using SVG image, you can keep the size of the document small. Please note that attaching large raster graphics like JPEG, PNG etc. to the mindmap may considerably increase the size of the resultant PDF document.

### Warnings

If some kind of warning-text is to be rendered, then that node should be annotated with stop icon (![stop icon](docs/examples/blooper-specs/images/stop.png)), and the warning-text should be placed as a note in that node. Then this text would be rendered prominently in a frame-box. This annotation should be used mainly for sections where some kind of questions or doubts are to be raised and marked in the document.

### Marked as New

If some text is to be flagged as new, then annotate respective nodes using addition icon (![addition icon](docs/examples/blooper-specs/images/addition.png)). Such blocks of text would be marked as New for easy identification. This can be used to indicate any newly added section in the document.

### Marked for Removal

If any block of text elements rendered using a node is to be marked for removal in future, then annotate that node with Not OK icon (![Not OK icon](docs/examples/blooper-specs/images/cross.png)). Then the content of this and its children would be distinctly marked for removal using red text and lines. In program specifications, it would be a good practice to indicate such blocks of text before they are actually removed in the next version of the document. This flag can also be used for marking deprecated sections in the document. The actual text to be used for this purpose (Delete, Deprecated, To be Removed, etc.) can be defined via the configuration parameter

### Database Schema

If a particular node is annotated with File_doc_database icon (![File_doc_database icon](docs/examples/blooper-specs/images/db.png)), all children of it would be considered as containing details of database schema. There are various conventions which are to be followed to prepare a DB schema. They are mentioned below:

- All nodes which are direct children of this annotated node are treated as names of the database tables.
- All child nodes of those table-nodes are treated as names of the fields in that table.
- The field-nodes must be written following certain conventions, which are listed below:
  - The structure of the text in fields must be of the form `field_name: field_options`
  - The field-options must be separated with commas(,).
  - If an outgoing arrow from a field goes to another field of same or different table, then the former is treated as a foreign key field.
  - If an incoming arrow comes to a field from another field, then it is assumed that the former is the primary key field of that table.
  - The arrows from nodes which are part of DB schema can not point to any node which lie outside the starting node of that schema.
  - The behavior of incoming arrows to any table-node from any node which are not part of the same DB schema is not well defined at the moment. Same is the case for field-nodes too.
  - The field-options can be one or more of the following, duly separated by commas:
    - pk: Primary Key
    - int: Integer data type
    - integer: Integer data type
    - enum: Enum data type
    - tinyint: 8 bit integer
    - smallint: Small sized integer
    - mediumint: Medium sized integer
    - bigint: Big integer
    - int8: 8 bit integer
    - int16: 16 bit integer
    - int32: 32 bit integer
    - int64: 64 bit integer
    - text: Text
    - geocolumn: Lat-Long data type
    - char(N): N number of characters
    - varchar(N): N number of varchar type data
    - bool, boolean: Boolean data type
    - float: Single precision floats
    - double: Double precision floats
    - real: Real number
    - decimal: Decimal number
    - json: JSON data
    - date: Date
    - datetime: Timestamp
    - ai: Autoincrement
    - unique: The value of this field must be unique within the table
    - default: Default value for this field
    - null: The value is nullable
    - not null: The value can not be null

### UML Usecase Diagrams

You may generate high-quality vector diagrams of usecases from your mindmaps.
Sample mindmap and respective pages from the resultant document are given below.

You may define a set of actors in your mindmap as shown below. The parent node,
holding them can be marked to be ignored using a broken-line icon, so that it
won't get rendered in the resultant document.

![Actors Node](docs/examples/blooper-specs/images/actors.png)

The usecase-nodes can be created using as shown below. They need correct
fpcBlockType attribute set in them. (You may do this via suitable templates as
described later in this document.)

![Usecase Nodes](docs/examples/blooper-specs/images/usecases.png)

The rendered pages using these actors and usecase-nodes are shown below. The UML diagrams and the flows defined for each usecase are rendered cleanly in respective sections of the document.

![Usecase Details - Page 1](docs/examples/blooper-specs/images/usecase-page1.png)
![Usecase Details - Page 2](docs/examples/blooper-specs/images/usecase-page2.png)
![Usecase Details - Page 3](docs/examples/blooper-specs/images/usecase-page3.png)

You may create various usecase-specific nodes dynamically using appropriate
templates. The templates used to create the sample mindmap are shown below.

![Templates for Usecase Specific Nodes - 1](docs/examples/blooper-specs/images/template-definitions-1.png)
![Templates for Usecase Specific Nodes - 2](docs/examples/blooper-specs/images/template-definitions-2.png)

For generating proper usecase diagrams, following node-attributes must be set on applicable nodes.

- fpcBlockType: It should possess values like UCPackage, UCActors, UCAction, etc. for respective nodes.
- fpcUCPDirection: It decides the flow-direction of arrows from actors to usecases. It can be either LR (left to right), or TB (top to bottom).
- fpcNotesDirection: It decides the direction of note-bubble. It can be LO (left of), TO (top of), RO (right of), BO (bottom of) the elements to which the note is getting attached in the diagram.

This can be done automatically using the [Dynamic Type Creater](https://github.com/i-plasm/freeplane-types-creator) script along with sample "Templates" node found in [Blooper Specifications](https://github.com/kraghuprasad/fp-convert/raw/main/docs/examples/blooper-specs/Blooper_Specifications.mm) mindmap.

### List of Track Changes

As discussed earlier, you may annotate certain nodes as newly added, and some others as marked for removal. They would be duly indicated in the document with appropriate icons and marker texts. It is also possible to collate a list of all such changes and render them in a neat table along with respective hyperlinks for cross references. For rendering this table, you need to supply the key "Trackchange_Section" in document's meta data in the notes of its root node. The value supplied for this key would be used to name a section created at the end of the document for rendering the list of all those changes in a tabular view. If you want to position this section as a named node in some other parts of the document - like in the beginning of the document itself - then create a node with an appropriate section-name and annotate it with the inverted red triangle icon (![Inverted Red Triangle icon](docs/examples/blooper-specs/images/inverted_red_triangle.png)). In this case the value supplied against the key "Trackchange_Section" in the document's meta data would be ignored and the table would be rendered in the position where that node is defined. Please note that if you annotate more than one node to render the track-changes, then an exception would be raised, as only one such section per document is allowed. Also if you do not supply the key "Trackchange_Section" in the document's meta data, then even annotating any node with the inverted red triangle icon would not generate the intended table containing the list of track-changes.

### Ignore Sections and List-items

If a particular node is annotated with broken line icon (![broken line icon](docs/examples/blooper-specs/images/broken.png)), then contents of it and all its children would be ignored while building the PDF document.

## Additional Text

Besides rendering the contents of nodes, additional text can be included as note-text in each node. Depending on the way the node is annotated (or not), those note-texts would be rendered too in the resultant PDF file.

## Sample Mindmap and PDF Document

You may download and use the sample mindmap [Blooper_Specifications.mm](https://github.com/kraghuprasad/fp-convert/raw/main/docs/examples/blooper-specs/Blooper_Specifications.mm) which is shared with the sources of this application to learn, explore and try out various formatting options described above. The PDF file generated from this mindmap is available as [Blooper_Specifications.pdf](https://github.com/kraghuprasad/fp-convert/raw/main/docs/examples/blooper-specs/Blooper_Specifications.pdf). The first-time users are advised to use these samples to explore the features of fp-convert before making their own mindmaps.

## Future Plans

This code can reasonably be extended to include additional document types. For example it would be possible to come up with a schema for composing music using freeplane, and it could be rendered as sheet music using MusiXTeX. Similarly using CircuiTikz, one can come up with a scheme to build and render electronic circuit too. Similar possibilities are endless. If one can design a convention to build a mindmap and define a template to render its content using TeX/LaTeX, a class equivalent to psdoc.py can be integrated and included as part of fp-convert.
