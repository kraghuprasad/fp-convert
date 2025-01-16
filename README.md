# fp-convert

If you use mindmaps to capture and manageme knowledge, but others working with you find them quite cumbersome to read and understand, then fp-convert is for you. It converts a freeplane mindmap to print-quality PDF. At present it converts a mindmap to a project specification document. The same template can be used to build any knowledgebase and print it out as a beautiful PDF document. It uses LaTeX document as its intermediate format before converting it finally into a PDF file.

Following image summarizes what fp-convert can do if it is provided with a suitably prepared freeplane mindmap.
![fp-convert [options] mindmap-file pdf-file](docs/examples/blooper-specs/images/fp-convert-summary-image.png)

## Why?

In last few decades, people have various options when selecting their tools for knowledge management. Till a decade back, majority of documents were created using word processors like MS Word or Libre Office or something similar. Today they have evolved into their online avatars which entirely reside on the cloud and can be accessed using a web browser. Google Workspace is one such example, using which documents, spreadsheets, and presentations can be created and stored easily. Once upon a time, people used to understand that there exists a separation between contents of a document and its representation. But that has mostly been blurred for majority of people today who jump onto any available tool to capture and maintain information. Until we understand this separation, it would not be possible to select the most suitable tool for our knowledge management needs.

While dealing with projects, especially software projects, we regularly find people capturing and maintaining functional and program specifications in Word docs, Excel spreadsheets and (Horror!!!) Powerpoint presentations. Those who have used such tools to write project specifications also know the inherent challenges in maintaining them over a long period of time, sometimes stretching over decades. Some of the common problems associated with these kinds of tools are listed below.

- It takes a lot of efforts to focus on certain sections of the specifications document while modifying it. The specifications are mostly inter-related, and changing one section may have its own side effects on other sections of the document.
- Navigating through a large document, spreadsheet or presentation itself makes the whole process quite tedious. For example while looking at a particular response obtained from an API call, one may want to know the relevance of certain data point which is part of the response. Those details might have been stored somewhere in the functional specifications section in the same document. Linking those sections, and then maintaining them properly throughout the project execution and maintenance period may not be simple. Due to large spread of the content, people may find it difficult to separate and focus only on the affected sections (this is easily handled in mindmaps, by the way) of the document.
- While writing the content of the document, using different versions of the same tool on different machines may result in changes in the document-styles. Such changes are visible mostly in the fonts and font-styles. This creates an unwanted distraction or jarring effect on the reader who wants to focus on the content rather than on its presentation.
- If multiple people are formatting a document over a long period of time, their styles of writing as well as formatting starts changing. In large specification documents which has passed through multiple hands over the yeras, you may find that some section of the document being formatted in fixed sized fonts, while the similar content being formatted with variable sized fonts. The fonts and formatting, if assists in better readability and understanding of the content of the document, then it good. Otherwise they just add only to the clutter. A badly formatted document becomes unreadable quickly, and people would lose interest in maintaining it, unless forced to do so. We all know that anything forced on to the people do not last long.
- Except PDF, HTML, or Markdown text, there exists no standard document formats which render properly on multiple viewers running on different operating systems. For example, documents or presentations create using Microsoft tools on Windows OS do not render properly in tools provided by say, Libre Office on Linux OS, even if those file formats are stated to be supported by it. This itself should be sufficient enough to discard such tools for managing the knowledge associated with a project. Forcing people to opt for a particular tool and OS to access common documents helps only to prop-up vendors of such tools and OS, not to the users who really need those douments.

To solve these problems, TeX/LaTeX is a good tool, which allows us to maintain the separation between content and style. It is possible to convert a TeX based document to corresponding PS or PDF file formats, which are known as portable file formats. They are guaranteed to render correctly everywhere. Now a days, a scaled down version with very limited formatting features are found in Markdown or XML based text editors too.

While writing the document, the author can decide to chose the right format to display a particular content. For example, the same content can be formatted in a tabular form (in spread-sheets), in paragraphs of text (in word docs), flowcharts (using Visio or LibreDraw) or in any other suitable form. This is the prerogative of the producer (author) to decide how certain content should be rendered to convey the required information to the reader of the document. This requires good understanding on the producer's part on what to show what in which format. The lack of such understanding, along with misuse of existing text or data formatting tools have actually blurred the line of distinction between content and its presentation today. We regularly find badly formatted documents where even the section-headers are not properly structured. Many consider that the headers of a section means just few phrases formatted in bold-text. This kind of formatting makes it impossible to auto-generate the table of contents of a large document along with its section-headers and page numbers.

TeX/LaTeX also ensures that if we use its predefined document templates prudently, then the resultand documents are prepared following all pertinent typesetting rules. Since most of the people are not familar with the rules of typesetting, it is always better to leave that job to a suitable tool like TeX. Proper typesetting is mandatory for a document to make its content easily accessible to the consumers of that document.

Though it is easy to generate any kind of document using WYSIWYG text editors, there are scenarios where the end results may not turn out to be useful for the consumers of those documents. One such scenario is writing functional or implementation specifications of a project or creating a database schema for it. Design being a non-liear activity, it is required to add or remove contents in that documents, while maintaining required cross-referencing between its sections. This is required not only during the design and development periods of such applications, it might be needed to be done for every change-requests received from the client after it has gone to the production. The authors of specifications know that such documents need extensive cross references, various kinds of diagrams, tables, lists of entities etc. to define the underlying functional or implementation concepts. Though we can create such content in plain text, soon it becomes tedious to maintain it for a long period of time. Sometimes such documents are to be updated and maintained for decades. Those who have worked with TeX/LaTeX would know how much extra text one has to write and maintain to just create cross references among sections, tables, lists etc. Besides that, one needs to know basic concepts of TeX to debug issues which may crop up during the document compilation phase.

A lot of above mentioned problems can be fixed by opting for a mindmap based approach while creating any project specifications. Mindmaps have turned out to be quite useful to brainstorm ideas, and to design solutions for various problems. If we create all our specifications in mindmaps while following certain conventions, fp-convert can generate properly typeset document from it which is portable as well as which would render correctly on all devices and operating systems. The text (XML) based mindmaps created by freeplane is easy to store in any repository like git subversion etc. along with the application's source code, its configuration, and other assets. This central storage of all assets together also helps in ensuring single source of knowledge for the whole project.

## License

This application is released under Apache(v2) License. You are free to use its code in commercial as well as in open source projects, under pertient licencing terms. But please note that one of the components used in this project ([freeplane-python-io](https://github.com/nnako/freeplane-python-io)) is released under GPLv3. This may affect your chances of using this tool along with non-GPLed code - like in a proprietary tool. But if you are using this tool as a standalone application executed via command line without linking it directly to your product's codebase, then probably you are free to use it in your commercial products too. But it would be prudent to consult a lawyer familiar with IP and software licenses before opting for that approach.

## Usage

Executing `fp-convert -h` results in its help-text getting displayed.

---

```
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
Apprropirate options are provided using which the TeX file generated by this
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

## Software Components

fp-convert is standing on the shoulders of giants like Python and TeX/LaTeX which doesn't need any introductions. But two critical components without which this endeavour would not have been possibe are [PyLaTeX](https://github.com/JelteF/PyLaTeX) and [freeplane-python-io](https://github.com/nnako/freeplane-python-io) (thanks nnako for all those timely help :).

## LaTeX Envirnoment

It would be the safest bet to install full tex-live package on the host on which this program is to be executed. Or at least a TeX/LaTeX environment with all the following packages installed:

- texlive-base
- texlive-latex-base
- texlive-latex-recommended
- texlive-fonts-recommended
- texlive-fonts-extra
- texlive-latex-extra
- texlive-pictures
- texlive-science
- texlive-latex-extra

But if you have a scaled down TeX/LaTeX environment on your system, then please make sure that you have the following TeX packages installed on it:

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

You will also need to install all those additional TeX packages on which the commandline-options to fp-convert depends on. For example, you may need to install additional font-packages, if you are not satisfied with `lmodern` or `roboto` font-family for your document. In such case, you may also need to install additional fonts on your system. That's the reason it is best to install full tex-live package on the host, even though it is a large package which consumes a lot of disk space.

Please note that this program was built and tested on Manjaro Linux which is based on Arch Linux. It is also expected that it will work without any issues on other Linux distributions like Debian, Ubuntu, Fedora and all other distros built using them. In fact it should work with any unix-like system like FreeBSD, OpenBSD, NetBSD, DragonFlyBSD, etc. It may also work on Windows and MacOS, provided all required TeX and other Python packages are available on them. Your milage may vary though. We would like to hear the experience of users who could get it working on Windows and Mac.

## Features

fp-convert is a commanline tool written in Python which uses fp_convert module to carry out its work. The same module can be invoked from other Python programs too, to generate required PDF documents. At present it is designed to generate project specification document for any software or IT based projects. We would be adding support for other kinds of documents in future, based on the demand from the community. At the same time it should not be presumed that the generated document would not be useful for capturing other knowledge-items. fp-convert uses LaTeX base document class `article'. Hence you can use fp-convert to generate any kind of document which can be built using that document class, as long as you follow certain conventions while creating your mindmap.

### Print-Quality PDF Generation

fp-convert can generate PDF file using TeX/LaTeX text processing system. It creates beautiful, and compact documents which follow almost all typographic conventions followed in a standard TeX based document template.

### Document's Data and Metadata

The document's content is kept separate from the standard meta-data like page-geometry, logo-images and their dimentions, colors of various artifacts etc. Following is the meta-info stored in the root node of the sample mindmap. This is fetched and processed automatically by fp-convert and rendered in the resultant PDF file at appropriate places.

---

```
Title: Project Specifications of Blooper App
Version: 1.2
Date: 15 November, 2024
Author: Whoopie Bard $<$whoopie@clueless.dev$>$\\Changu Bhai $<$changu.bhai@clueless.dev$>$
Client: Blooper Corporation Inc.
Vendor: Clueless Developers' Consortium
TP_Top_Logo: images/blooper_logo.pdf
TP_Bottom_Logo: images/clueless_devs_consortium.pdf
C_Header_Text: Project Specifications of Blooper App
R_Header_Text: Non-Confidential
L_Header_Logo: images/blooper_logo.pdf
C_Footer_Logo: images/clueless_devs_consortium.pdf
R_Footer_Text: \small{Page \thepage\- of \pageref*{LastPage}}
Header_Thickness: 0.4
Footer_Thickness: 0.4
```

---

There are additional controls too are possible, which are not readily available here. For example, by creating your own Theme, Color, Config classes, you can control the resultant document in much more fine grained manner. Also it is possible to supply all such configurations in a YAML based configuration file which can be passed to the program using -c option on the commandline.

At present, the documentation is quite sparese. But we hope to improve it over some time.

### Sections, Subsections, and More

Except root node, all following nodes in a mindmap are treated as sections, their subsections, their subsubsections and more. You can attain maximum depth of 5 in this manner. The node's text is treated as header of respective sections, and the note-text in each of them are rendered as section-content. Every linke-break in the note-text is taken as the start of a new paragraph in respective section. If a node is to be treated in a different way, it should be annotated with a suitable icon.

### Unordered Lists

If a node is annotated with list icon (![list icon](docs/examples/blooper-specs/images/list.png)), a nested bullet-list (generated by LaTeX's \itemize) is created using its children and their respective children. The depth of list can be up to 3.

### Ordered Lists

If a node is annotated with list icon (![list icon](docs/examples/blooper-specs/images/list.png)) as well as input numbers icon (![input numbers icon](docs/examples/blooper-specs/images/numbers.png)), then the list created from the contents of the direct children of that node would be an ordered list. The depth of the list is not dependent on the type of the list. Overall the total depth can not be more than 3, irrespective of whichever types of lists are mixed and matched. Also annotating a node without list icon but with input numbers icon would not generate an oredered list unless at least one of the parent-node between that node and the root node is annotated with the list icon. It means, starting an ordered list with a node annotated only with the input numbers icon would not be possible. Please refer the sample mindmap provided with fp-convert how such lists work.

### Tabular Views

By annotating any node with generic icon (![generic icon](docs/examples/blooper-specs/images/table.png)), a tabular view can be built. The first level of children after that node would be rendered as first column of respective rows in that table. The second level onwards the nodes would contain the column header and content for second column onwards. Each such row should contain the text in X:Y format, where X would be the column header, and Y would be the column-value. Check the sample mindmap and the resultant PDF file to know how the contents are placed and rendered.

### JSON/XML/HTML/Verbatim/Code Blocks

By annotating any node with JSON icon (![json icon](docs/examples/blooper-specs/images/json.png)), a verbatim block can be created from its content using LaTeX's verbatim environment. Please note that the whole node's content would be rendered in verbatim mode. This kind of rendering is suitable to display HTML, XML, JSON, as well as software code.

### Images

If an image is to be rendered in a particular section or subsection, then node corresponding to that section should be annotated with image icon (![image icon](docs/examples/blooper-specs/images/image.png)). The raster image formats like JPEG and PNG are supported. If you want to use vector graphics, then attach SVG based images. They would be auto-converted to PDF and used in the resultant PDF document.

### Warnings

If some kind of warning-text in red is to be rendered, then that node should be annotated with stop icon (![stop icon](docs/examples/blooper-specs/images/stop.png)), and the warning-text should be placed as a note in that node. Then this text would be rendered in a red box for easy identification.

### Marked as New

If some text is to be flagged as new, then annotate respective nodes using addition icon (![addition icon](docs/examples/blooper-specs/images/plus.png)). Such blocks of text would be marked as New for easy identification.

### Marked for Removal

If any block of text elements rendered using a node is to be marked for removal in future, then annotate that node with Not OK icon (![Not OK icon](docs/examples/blooper-specs/images/cross.png)). Then the content of this and its children would be distinctly marked for removal using red text and lines.

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
  - The behaviour of incoming arrows to any table-node from any node which are not part of the same DB schema is not well defined at the moment. Same is the case for field-nodes too.
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

## Additional Text

Besides rendering the contents of nodes, addtional text can be included as note-text in each node. Depending on the way the node is annotated (or not), those note-texts would be rendered too in the resultant PDF file.

## Future Plans

This code can reasonably be extended to include additional document types. For example it would be possible to come up with a schema for composing music using freeplane, and it could be rendered as sheet music using MusiXTeX. Similarly using CircuiTikz, one can come up with a scheme to build and render electronic circuit too. Similar possibilities are endless. If one can design a convention to build a mindmap and define a template to render its content using TeX/LaTeX, a class equivalent to psdoc.py can be integrated and included as part of fp-convert.
