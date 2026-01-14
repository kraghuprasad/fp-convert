version: 0.3.0

# fp-convert 

## Introduction

The fp-convert uses TeX/LaTeX to generate beautiful print-quality documents from the content obtained from [Freeplane](https://docs.freeplane.org/) mindmaps.

If you use mindmaps to capture and manage information, but others working with you find them quite cumbersome to read and understand, then fp-convert is for you. It converts a [Freeplane](https://docs.freeplane.org/) mindmap to print-quality PDF documents, provided the attribute fpcBlockType of its nodes are properly annotated with valid block-types. At present it supports rendering following block-types:
- DBSchema: Tables, fields and other details of database schema
- Default: Section, Subsection, SubSubSection, ... up to five levels
- Deliverable: The deliverable of a project
- Ignore: Ignores rendering of the node and its children
- Image: Scalar and vector image
- NumberTable: Table with summable columns
- OrderedList: Numbered list
- PageBreak: New page
- PlainText: Plain text
- Risk: Risk in a task or project
- StopFrame: Warning-text in a frame
- Table: Table to display textual data
- TrackChanges: Change-set trackers based on appropriately annotated nodes
- UCAction: UML usecase action
- UCActors: UML actors (a numbered list, at present)
- UCPackage: UML package
- UnorderedList: Bullet-list
- Verbatim: Textual blocks rendered as it is with monospaces font

Following image summarizes what fp-convert can do if it is provided with a suitably prepared freeplane mindmap.
![fp-convert [options] mindmap-file pdf-file](docs/images/fp-convert-summary-image.png)

## Document Structure

Once upon a time, people used to understand that there existed a separation between contents of a document and its representation. But that has mostly been blurred for majority of people today who jump onto any available writing or presentation tool to capture and maintain information. Until we understand this separation, it would not be possible to select the most suitable tool for any knowledge management needs. While dealing with projects - and specifically software projects - we regularly find people capturing and maintaining functional and program specifications in Word docs, Excel spreadsheets and (Horror!!!) Powerpoint presentations. Those who have used such tools to write project specifications also know the inherent challenges in maintaining them over a long period of time, sometimes stretching over decades. Some of the common problems associated with these kinds of tools are listed below.

- It takes a lot of efforts to focus on certain sections of the specifications document while modifying it. The specifications are mostly inter-related, and changing one section may have its own side effects on other sections of the document, which may be tens of pages away from the current one. Then it becomes a repetitive jumping between various pages, sections, tables, and images while modifying a document.
- Navigating through a large document, spreadsheet or presentation itself makes the whole process quite tedious. For example while looking at a particular response obtained from an API call, one may want to know the relevance of certain data point which is part of the response. Those details might have been stored somewhere in the functional specifications section in the same document. Linking those sections, and then maintaining them properly throughout the project execution and maintenance period would not be easy. Due to the content-spread, people may find it difficult to isolate and focus only on the affected sections (this is easily handled in mindmaps, by the way) of the document.
- While writing the content of the document, using different versions of the same tool on different machines may result in changes in the document-styles. Such changes are visible mostly in the fonts and font-styles. This is not expected in well built prepared documents.
- If multiple people are formatting a document over a long period of time, their styles of writing as well as formatting starts changing. In large documents which have passed through multiple hands over the years, it is common to find various sections of the document getting formatted with different font-families. The fonts and formatting are considered good if they are used to correctly to convey intended information clearly. Otherwise, they just add only to the clutter. People would lose interest in maintaining cluttered and badly formatted documents. Unmaintained documents are as good as no documents.
- Except PDF, HTML, or Markdown text, there exists no standard document formats which render properly on different document-viewers running on different operating systems. For example, documents or presentations created using Microsoft Office on Windows do not render properly in Libre Office running on Linux or Unix-like systems; even though such file formats are stated to be supported by it. This itself should be sufficient to discard those tools for long term knowledge management. Forcing everyone to opt for a particular OS or program to access a particular document helps only to prop-up the bottomlines of respective companies which create those OS and tools with all kinds of vendor specific and non-standard lock-ins. It does not serve well the users of those documents.

To solve these problems we can opt for TeX/LaTeX as our preferred documentation tool. It is fully open source and it also allows us to maintain the separation between content and style in the documents. It is possible to convert a TeX based document to corresponding PS or PDF files, which are known as portable file formats. They are guaranteed to render correctly everywhere and there exists many open-source as well as proprietary tools to view them on different kinds of devices. Modern PDF documents support hyperlinks which are essential for cross-referencing within sections of the same document.

While writing the document, the author can decide to chose the right format to display its content. For example, the same content can be formatted in a tabular form (in spread-sheets), in paragraphs of text (in word docs), flowcharts (using drawio, visio or libredraw) or in any other suitable form. This is the prerogative of the producer (author) to decide how certain content should be rendered to convey the required information to the consumer (reader) of the document. This requires good understanding on the producer's part to convert data into suitable information. We find that the lack of such understanding, along with misuse of existing text or data processing tools have actually blurred the line of distinction between content and its presentation. We regularly find badly formatted documents where even the section-headers are not suitably defined. Many treat the headers of a section as mere text-blocks formatted in bold-style. This kind of formatting makes it impossible to auto-generate the table of contents of a large document along with its section-headers and page numbers. If we define the structure of the documents correctly, then existing text processing tools like TeX/LaTeX, Microsoft Word, Libreoffice Writer; or cloud based text editors like Google Docs, O365 Word etc. would be able to auto-generate the table of contents for us. Such ToC contains properly hyperlinked sections, which can take the user to their respective page numbers.

## Why TeX?

Proper typesetting of the supplied content is necessary to make a document easily comprehendable to its readers. TeX/LaTeX provides advanced text processing capabilities which makes its users to focus mostly on the content and structure of the document, while it takes care of applying correct typesetting rules to while building the document. Using various standard document templates prudently, we can ensure that the resultant document would get built correctly without any special interventions from us. Since many people are not familiar with the rules of document typesetting, it is always better to leave that job to a suitable tool like TeX. 

Though it is easy to generate any kind of document using WYSIWYG text editors, there are scenarios where the end results may not turn out to be useful for the consumers of those documents. Following are some of the examples of scenarios, where careful selection of document format is important:

- Imagine writing the functional or implementation specifications of a project. For this, usually people resort to MS Word, Excel sheets or Powerpoint presentations. Each of them have their own set of problems to capture and manage the information pertaining to a project. Once the document becomes large, cross-referencing its content becomes are big problem. Developers are forced to access such documents in a non-linear manner. While reading the program specifications of an API, it would be quite handy to access concerned database schema with a single-click. Usually it takes a lot of efforts to maintain such references within the document which gets updated by multiple people during the course of execution of a project.
- Another example is about maintaining the schema of a relational database used in an enterprise application. It is important to ensure that the details of the schema is made available to the developers in a concise format which should be easy to comprehend within a short period of time. It too requires cross-referencing between primary and foreign keys used in different tables. A spreadsheet or a presentation slide may not be the most suitable format to capture and render such information to the people.
- Preparing a usecase diagram is easy using a diagramming tool. But how can one introduce such diagrams within a functional specification document in such a way that when the usecase changes, respective diagrams too get updated and get inserted at the right place automatically?
- Those who have created minutes of meetings know the depth up to which one needs to go to capture and track action-items, delivery-dates for each of them, and concerned actors who would be working on them. It is also required to capture and track older an incomplete action-items in newer meetings. Unless a suitable application is used to cross-link and track those meetings and their respective MoMs, it is not easy to manage them using a single document. 

There are multiple scenarios where the document formats used commonly don't suffice to take care of underlying issues. The fp-convert tool is a document generation tool, which can be employed to manage some of the scenarios mentioned above. It is evolving in its functionalities, and over a period of time, it is expected to cover many more scenarios to capture, maintain and render information in different fields of operations.

## Documentation Tool for System Architects

In this section we would focus on documentation tools suitable for system architecture and design. For many decades now, the mindmaps have turned out to be quite useful to brainstorm ideas, and to design and document solutions for various problems. If one writes the project specifications in a mindmap, while following certain conventions, the fp-convert can generate properly typeset document from it. The resultant document would be portable across all major operating systems. Also the text (XML) based mindmap created by Freeplane can be easily stored in any code and configuration repository like git, subversion, VSS etc., along with other project assets. This ensures single source of knowledge for the whole project under strict version-controls.

Almost all kinds of designing is a non-linear activity where a person focuses on certain aspect of a design for certain period of time, and then jumps over to another aspect to work on for another stretch of time. While working on the design document of a system, it is required to add or remove sections too in a non-linear manner. While doing so, it is important to maintain required cross-references between its sections correctly. This is required not only during the design and development phase, but also needed to be done for every change-requests received from the client after the application has gone in production. The system specifications may need various kinds of diagrams, tables, lists of entities etc. along with respective descriptive texts to define the underlying functional or implementation specific details. Though we can create such contents in plain text using any WYSIWYG text processor, soon it becomes tedious to maintain it for a long period of time. Sometimes such documents are to be updated and maintained for decades. Even using TeX/LaTeX to create it would make that work quite tedious and cumbersome as user is forced to write long lines of LaTeX specific texts or commands to control the style of the text-blocks. For example, LaTeX requires the following four lines to render a bullet-list containing two items:

Some may suggest to opt for markdown text, instead of LaTeX. But the documents generated directly from markdown text look quite bland in terms of their styles. The PDF pages generated from markdown texts do not look like professionally type-set ones. The markdown is more suitable to get converted to an HTML document which can be rendered well in a web browser.

Besides such verbosity required in LaTeX, it is also a pain to create and maintain cross references among sections, tables, lists etc. It requires large amount of text-elements to define labels and hyperlinks. Besides that, one needs to know basic concepts of TeX quite well to debug issues which may crop up during the compilation of the document. These problems can be avoided by avoiding direct use of LaTeX and using fp-convert instead.

## The Swiss Army Knife for Document Generation

The solution to these kinds of problems lies in selecting two separate tools for writing and reading. One can use a mindmap to capture and maintain the information, where it allows the author to focus on specific nodes while writing. By linking these nodes together, one can create a well cross-referenced document, without taking much pain. The nodes of the mindmap requires certain kinds of annotations, which can easily be provided by using suitable template in the same mindmap. New annotated nodes can be created quickly using the excellent [Dynamic Types Creator](https://github.com/i-plasm/freeplane-types-creator) script built for Freeplane by the open source community.

By converting that mindmap into a properly cross-referenced PDF document, one can avoid almost all kinds problems listed above. That's what fp-convert does. It converts mindmaps created by Freeplane into correctly formatted documents in PDF format. Using supplied templates and script, one can quickly prepare the base mindmap for very complex documents containing even hundreds or thousands of sections, tables, and images; which would get converted to a proper print-quality PDF file using fp-covert.

## License

This application is released under GNU Public License (v3).

## Installation

fp-convert is standing on the shoulders of giants like Python and TeX/LaTeX which don't need any introductions. But two critical components without which this endeavor would not have fructified are [PyLaTeX](https://github.com/JelteF/PyLaTeX) and [freeplane-python-io](https://github.com/nnako/freeplane-python-io) (thanks nnako, for all those timely help provided by you :).

This program requires a recent version of Python3 (already tested on Python 3.13) to work. You may install it on the system-provided Python or on a Python virtual environment. For system-wide installation from Python package repository, please execute the following command on the console.

```bash
pip install fp-convert
```

It will download all Python based dependencies automatically. But you also need a fully functional TeX/LaTeX environment installed on your machine to use this tool. It is freely available for all major operating systems. Please refer your OS manual or the support provided by user-communities on the Internet to know how to install TeX/LaTeX on your favorite operating system.

On Linux based machines, you may find that following tex-packages get installed as part of a full TeX installation:

- texlive-base
- texlive-latex-base
- texlive-latex-recommended
- texlive-fonts-recommended
- texlive-fonts-extra
- texlive-latex-extra
- texlive-pictures
- texlive-science
- texlive-latex-extra

If full texlive package is not available on your machine due to disk-space crunch, or due to some other reason; then at least a TeX/LaTeX environment with following packages must be made available for fp-convert to work properly:

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
[It is possible that versions of fp-convert released in future may add or remove some of the items in this list.]

You should also install all those additional TeX packages on which the command-line-options to fp-convert depends on. For example, you may need to install additional font-packages, if you are not satisfied with the default `lmodern` or `roboto` font-family for your documents. In such case, you may need to install additional fonts on your system.

If you are planning to generate UML usecase diagrams too, then you must install [PlantUML](https://plantuml.com/) on you machine. Adding node-level attributes required by fp-convert to generate UML diagrams or many other document-elements may turn out to be quite boring chore. To ease that process, [i-plasm](https://github.com/i-plasm) and [euu2021](https://github.com/euu2021) have collaborated to create an excellent groovy script named [Dynamic Types Creator](https://github.com/i-plasm/freeplane-types-creator) which should be placed in the scripts folder of your [Freeplane](https://docs.freeplane.org/) installation folder. You should map a keyboard shortcut -- I use "Alt+t" -- to run Dynamic Type Creator script on a selected node. This can be configured from within the freeplane program by going to "Tools -> Assign hot key", then selecting applicable script, and then pressing those keyboard shortcuts to register it in Freeplane. Please refer the documentation of [Freeplane Hot Keys](https://docs.freeplane.org/user-documentation/hot-keys-and-beyond.html) for further information on installation, configuration and enabling keyboard shortcuts for any script based plugins.

You should download [Template_Repository.mm](https://github.com/kraghuprasad/fp-convert/blob/main/docs/examples/Template_Repository.mm), open it in freeplane, copy the required template-nodes from it, and paste the same into a node named "Templates" in the root node of your own mindmap to be used by fp-convert. You can leave the child-nodes of "Templates" node in collapsed state to minimize the distractions caused by it when you review the content of your mindmap. To avoid rendering the content of nodes under "Templates" from getting included in the resultant document, you may mark its fpcBlokType attribute to Ignore. You need to include only those node-templates, which you plan to use in your mindmap. Rest can be removed altogether. The details of syntax and semantics applicable to define such templates can be found in this [discussion thread](https://github.com/freeplane/freeplane/discussions/2365#discussioncomment-12807085).

## Operating Systems

This program was built and tested on a Desktop running Manjaro Linux. It is expected that it will work without any issues on other Linux distributions like Debian, Ubuntu, Fedora and other distros which are based on them. In fact it should work with any unix-like operating system like FreeBSD, OpenBSD, NetBSD, etc., provided all the software-dependencies of fp-convert are met. It may also work on Windows and MacOS, provided all required packages of TeX and Python are installed on it. Your mileage may vary though. The users who could get it working on BSD, Windows and Mac are welcome to share their experiences.

## Usage

Executing `fp-convert -h` results in its help-text getting displayed.

---

```txt
usage: fp-convert [-h] [-k] [-d]
                  [-f <font-family-name:font-family-options>]
                  [-c <config-file-path>]
                  [-g <config-file-path>]
                  [mindmap_file] [output_file]

Program to convert a Freeplane mindmap's content into a print-quality PDF
document. If only relative file-paths are used to define the resources (like
images) used in the mindmap, then run this program from within the folder in
which the mindmap file is situated. In case absolute paths are used in the
resource-paths within the mindmap, then this program can be executed from
anywhere, as long as appropriate input and output file-paths are provided to
it. By supplying option -k, the TeX file generated by this program can be
preserved for inspection and further customization of the document.
The generated TeX file can be recompiled using the program pdflatex in any
folder on the same machine on which fp-convert was executed to generate it.

positional arguments:
  mindmap_file          input freeplane mindmap file-path
  output_file           output PDF file-path

options:
  -h, --help            show this help message and exit
  -v, --version         show the version-number of fp-convert and exit
  -k, --keep-tex        keep intermediate TeX/LaTeX file for further review
  -f <font-family-name:font-family-options>, --font-family <font-family-name:font-family-options>
                        font-family to be used while building the PDF file
                        Correct LaTeX options are required to be passed-on
                        while supplying this parameter. Incorrect options, if
                        supplied, would result in TeX-compilation failures.
                        The option -k can be used to debug such issues by
                        preserving the resultant TeX file for further
                        inspection. Some of the valid values are given below
                        roboto (The Roboto family of fonts to be used),
                        roboto:sfdefault (The Roboto family along with LaTeX
                        option sfdefault),
                        roboto:sfdefault:scaled=1.1 (The Roboto family along
                        with LaTeX options sfdefault and scaled=1.1 which are
                        applicable on this font family),
                        roboto:scaled=1.1 (The Roboto family of fonts scaled to
                        1.1), etc.
                        Please ensure that invalid options for any font-family
                        do not get supplied here.
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

fp-convert is a command-line tool written in Python which uses fp_convert module to carry out its work. The same module can be invoked from other Python programs too, to generate required PDF documents. The LaTeX base document class `article' is used by fp-convert to generate the document. You may supply additional applicable options in the generated TeX file and recompile the same using pdflatex tool. You can use fp-convert to generate any kind of document which can be built using that document class, as long as you follow certain conventions while creating your mindmap. The details of those conventions are given in some of the sections below.

## Sample Mindmap and PDF Document

Few mindmaps are included in the fp-convert distribution, which can be studied
to understand its behaviour. They show how each of the annotations are to
applied, and how they get rendered in the resultant PDF document.

You may download and use the sample mindmap [Blooper_Specifications.mm](https://github.com/kraghuprasad/fp-convert/raw/main/docs/examples/blooper-specs/Blooper_Specifications.mm) which is shared with the sources of this application to learn, explore and try out various formatting options described above. The PDF file generated from this mindmap is available as [Blooper_Specifications.pdf](https://github.com/kraghuprasad/fp-convert/raw/main/docs/examples/blooper-specs/Blooper_Specifications.pdf). The first-time users are advised to use these samples to explore the features of fp-convert before making their own mindmaps.

## Future Plans

This code can reasonably be extended to include additional document types. For example it would be possible to come up with a schema for composing music using freeplane, and it could be rendered as sheet music using MusiXTeX. Similarly using CircuiTikz, one can come up with a scheme to build and render electronic circuits too. Similar possibilities are endless. If one can design a convention to build a mindmap and define a template to render its content using TeX/LaTeX/Tikz, a function to build that block-type can be implemented and included in the builders module of fp-convert.

The details of various content-blocks required to be set in the nodes of a Freeplane mindmap are provided in [The User Guide](docs/User_Guide.md) of fp-convert. You should study and understand it before converting your mindmap to PDF using fp-convert. You are requested to report all bugs found in fp-convert [here](https://github.com/kraghuprasad/fp-convert/issues).
