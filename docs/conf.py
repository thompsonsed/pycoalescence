# -*- coding: utf-8 -*-
#
# PyCoalescence documentation build configuration file, created by
# sphinx-quickstart on Mon Oct 24 17:19:28 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import re
import textwrap
from recommonmark.parser import CommonMarkParser

read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'

use_exhale = True # Change this if you don't want to run with exhale

if read_the_docs_build:
	try:
		from unittest.mock import MagicMock
	except ImportError:
		from mock import Mock as MagicMock


	class Mock(MagicMock):
		@classmethod
		def __getattr__(cls, name):
			return MagicMock()
	MOCK_MODULES = ['numpy', 'gdal', 'sqlite3', 'osgeo', "applyspecmodule", "necsimmodule", "necsimlinker"]
	if not use_exhale:
		MOCK_MODULES.extend(['exhale', 'configs'])
	sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
	sys.modules["scipy2"] = Mock()
	sys.modules["scipy2.spatial"] = Mock()
	sys.modules["scipy2.spatial.Voronoi"] = Mock()
	import scipy2
	from scipy2.spatial import Voronoi
if use_exhale:
	from exhale import configs



sys.path.insert(0, os.path.abspath('.'))
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../pycoalescence'))

import pycoalescence
# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
	'sphinx.ext.autodoc',
	# 'sphinx.ext.autosectionlabel',
	'sphinx.ext.doctest',
	'sphinx.ext.todo',
	'sphinx.ext.coverage',
	'sphinx.ext.mathjax',
	'sphinx.ext.ifconfig',
	'sphinx.ext.viewcode',
	'breathe'
]
if use_exhale:
	extensions.extend(['exhale'])

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Breathe project path
input_dir = "../docs/necsim_doc/xml/"
breathe_projects = {"necsim": input_dir}

# set the default project
breathe_default_project = "necsim"

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ['.rst', '.md']
# source_suffix = '.rst'
#
source_parsers = {
	'.md': CommonMarkParser,
}

# The encoding of source files.
#
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'pycoalescence'
copyright = u'2016, Samuel Thompson'
author = u'Samuel Thompson'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = re.sub(r"rc.*", "", pycoalescence.__version__)
# The full version, including alpha/beta/rc tags.
release = pycoalescence.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#
# today = ''
#
# Else, today_fmt is used as the format for a strftime call.
#
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README_necsim.rst', 'README.md',
					'*class_view_hierarchy.rst']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true,  produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
if not read_the_docs_build:
	html_theme = 'classic'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.
# "<project> v<release> documentation" by default.
#
# html_title = u'PyCoalescence v24/10/16'

# A shorter title for the navigation bar.  Default is the same as html_title.
#
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#
html_logo = "src/PyCoal_logo.png"

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#
html_favicon = "src/PyCoal_favicon_large.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#
# html_extra_path = []

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
#
# html_last_updated_fmt = None

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#
# html_additional_pages = {}

# If false, no module index is generated.
#
# html_domain_indices = True

# If false, no index is generated.
#
# html_use_index = True

# If true, the index is split into individual pages for each letter.
#
# html_split_index = False

# If true, links to the reST sources are added to the pages.
#
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr', 'zh'
#
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
#
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#
# html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'pycoalescencedoc'

# -- Options for LaTeX output ---------------------------------------------
preamb_old = r'''
  %\documentclass{memoir}
  \makeatletter
  \fancypagestyle{normal}{
	\fancyhf{}
	\fancyfoot[LE,RO]{{\py@HeaderFamily\thepage}}
	\fancyfoot[LO]{{\py@HeaderFamily\nouppercase{\rightmark}}}
	\fancyfoot[RE]{{\py@HeaderFamily\nouppercase{\leftmark}}}
	\fancyhead[LE,RO]{{\py@HeaderFamily \@title}} % here's the change
	\renewcommand{\headrulewidth}{0.4pt}
	\renewcommand{\footrulewidth}{0.4pt}
  }
  \makeatother
  %\color {blue}
  %\normalcolor {dark blue}
  \pagecolor [RGB]{255, 247, 226}
  \definecolor{VerbatimColor}{rgb}{0.95,0.85,0.65}
  \definecolor{VerbatimBorderColor}{rgb}{0.5,0.95,0.1}
'''
latex_elements = {
	# The paper size ('letterpaper' or 'a4paper').
	#
	# 'papersize': 'letterpaper',

	# The font size ('10pt', '11pt' or '12pt').
	#
	# 'pointsize': '10pt',

	# Additional stuff for the LaTeX preamble.
	#
	# 'preamble': preamb_old,

	# Latex figure (float) alignment
	#
	# 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
	(master_doc, 'pycoalescence.tex', u'pycoalescence Documentation',
	 u'Samuel Thompson', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#
latex_logo = "src/PyCoal_logo.png"

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#
# latex_use_parts = False

# If true, show page references after internal links.
#
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
#
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
#
# latex_appendices = []

# It false, will not define \strong, \code, 	itleref, \crossref ... but only
# \sphinxstrong, ..., \sphinxtitleref, ... To help avoid clash with user added
# packages.
#
# latex_keep_old_macro_names = True

# If false, no module index is generated.
#
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
	(master_doc, 'pycoalescence', u'pycoalescence Documentation',
	 [author], 1)
]

# If true, show URL addresses after external links.
#
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
one_line_description = "Runs and analyses spatially-explicit neutral coalescence simulations"
texinfo_documents = [
	(master_doc, 'pycoalescence', u'pycoalescence Documentation',
	 author, 'pycoalescence', one_line_description,
	 'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#
# texinfo_appendices = []

# If false, no module index is generated.
#
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#
# texinfo_no_detailmenu = False


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The basename for the epub file. It defaults to the project name.
# epub_basename = project

# The HTML theme for the epub output. Since the default themes are not
# optimized for small screen space, using the same theme for HTML and epub
# output is usually not wise. This defaults to 'epub', a theme designed to save
# visual space.
#
# epub_theme = 'epub'

# The language of the text. It defaults to the language option
# or 'en' if the language is not set.
#
# epub_language = ''

# The scheme of the identifier. Typical schemes are ISBN or URL.
# epub_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A tuple containing the cover image and cover page html template filenames.
#
# epub_cover = ()

# A sequence of (type, uri, title) tuples for the guide element of content.opf.
#
# epub_guide = ()

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#
# epub_pre_files = []

# HTML files that should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#
# epub_post_files = []

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# The depth of the table of contents in toc.ncx.
#
# epub_tocdepth = 3

# Allow duplicate toc entries.
#
# epub_tocdup = True

# Choose between 'default' and 'includehidden'.
#
# epub_tocscope = 'default'

# Fix unsupported image types using the Pillow.
#
# epub_fix_images = False

# Scale large images.
#
# epub_max_image_width = 0

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#
# epub_show_urls = 'inline'

# If false, no index is generated.
#
# epub_use_index = True


# Example configuration for intersphinx: refer to the Python standard library.
# Tell sphinx what the primary language being documented is.
primary_domain = 'py'

# Tell sphinx what the pygments highlight language should be.
highlight_language = 'py'

# def generateDoxygenXML(stripPath):
# 	'''
# 	Generates the doxygen xml files used by breathe and exhale.
# 	Approach modified from:
#
# 	- https://github.com/fmtlib/fmt/blob/master/doc/build.py
#
# 	:param stripPath:
# 		The value you are sending to exhale.generate via the
# 		key 'doxygenStripFromPath'.  Usually, should be '..'.
# 	'''
# 	from subprocess import PIPE, Popen
# 	if read_the_docs_build:
# 		try:
# 			doxygen_cmd   = ["doxygen", "-"]# "-" tells Doxygen to read configs from stdin
# 			doxygen_proc  = Popen(doxygen_cmd, stdin=PIPE)
# 			doxygen_input = r'''
# 				# Make this the same as what you tell exhale.
# 				OUTPUT_DIRECTORY       = ./Exhaled
# 				# If you need this to be YES, exhale will probably break.
# 				CREATE_SUBDIRS         = NO
# 				# So that only include/ and subdirectories appear.
# 				FULL_PATH_NAMES        = YES
# 				STRIP_FROM_PATH        = "%s/"
# 				# Tell Doxygen where the source code is (yours may be different).
# 				INPUT                  = ../PyCoalescence/NECSim/Documentation
# 				# Nested folders will be ignored without this.  You may not need it.
# 				RECURSIVE              = YES
# 				# Set to YES if you are debugging or want to compare.
# 				GENERATE_HTML          = YES
# 				# Unless you want it?
# 				GENERATE_LATEX         = NO
# 				# Both breathe and exhale need the xml.
# 				GENERATE_XML           = YES
# 				# Set to NO if you do not want the Doxygen program listing included.
# 				XML_PROGRAMLISTING     = YES
# 				# Allow for rst directives and advanced functions (e.g. grid tables)
# 				ALIASES                = "rst=\verbatim embed:rst:leading-asterisk"
# 				ALIASES               += "endrst=\endverbatim"
# 			''' % stripPath
# 			# In python 3 strings and bytes are no longer interchangeable
# 			if sys.version[0] == "3":
# 				doxygen_input = bytes(doxygen_input, 'ASCII')
# 			doxygen_proc.communicate(input=doxygen_input)
# 			doxygen_proc.stdin.close()
# 			if doxygen_proc.wait() != 0:
# 				raise RuntimeError("Non-zero return code from 'doxygen'...")
# 		except Exception as e:
# 			raise Exception("Unable to execute 'doxygen': {}".format(e))
# doxy_dir is the parent directory of what you specified in
# `breathe_projects[breathe_default_project]` in `conf.py`

# The configurations you specified
stripPath = ".."

internal_configs = textwrap.dedent('''
    # Tell doxygen to output wherever breathe is expecting things
    OUTPUT_DIRECTORY       = {out}
    # Tell doxygen to strip the path names (RTD builds produce long abs paths...)
    STRIP_FROM_PATH        = {strip}
'''.format(out=input_dir, strip=configs.exhaleDoxygenStdin))
# external_configs = textwrap.dedent(configs.exhaleDoxygenStdin)
# The full input being sent
full_input = "{base}\n{internal}\n\n".format(
    base=configs.DEFAULT_DOXYGEN_STDIN_BASE,
    # external=external_configs,
    internal=internal_configs
)

with open("README_necsim.rst", mode="r") as readme:
	data = readme.read()
if sys.version_info[0] != 3:
	data= data.decode('utf-8', 'ignore')
exhale_args = {
	"containmentFolder": "./necsim",
	"rootFileName": "necsim_library.rst",
	"rootFileTitle": "necim",
	"doxygenStripFromPath": stripPath,
	"afterTitleDescription": data,
	"createTreeView": True,
	"exhaleExecutesDoxygen": False,
	# "verboseBuild" : True
	# "exhaleDoxygenStdin": '''
	# INPUT=../pycoalescence/lib
	# OUTPUT={}
	# # If you need this to be YES, exhale will probably break.
	# CREATE_SUBDIRS         = NO
	# # So that only Doxygen does not trim paths, which affects the File hierarchy
	# FULL_PATH_NAMES        = YES
	# # Nested folders will be ignored without this.  You may not need it.
	# RECURSIVE              = YES
	# # Set to YES if you are debugging or want to compare.
	# GENERATE_HTML          = YES
	# # Unless you want it...
	# GENERATE_LATEX         = NO
	# # Both breathe and exhale need the xml.
	# GENERATE_XML           = YES
	# # Set to NO if you do not want the Doxygen program listing included.
	# XML_PROGRAMLISTING     = YES
	# # Allow for rst directives and advanced functions e.g. grid tables
	# ALIASES                = "rst=\verbatim embed:rst:leading-asterisk"
	# ALIASES               += "endrst=\endverbatim"
	# # Enable preprocessing and related preprocessor necessities
	# ENABLE_PREPROCESSING   = YES
	# MACRO_EXPANSION        = YES
	# EXPAND_ONLY_PREDEF     = NO
	# SKIP_FUNCTION_MACROS   = NO
	# # extra defs for to help with building the _right_ version of the docs
	# PREDEFINED             = DOXYGEN_DOCUMENTATION_BUILD
	# PREDEFINED            += DOXYGEN_SHOULD_SKIP_THIS
	# # ADDITIONAL
	# EXCLUDE_PATTERNS       = ../pycoalescence/lib/necsim/fast-cpp-csv-parser/* \
     #                     */necsim/fast-cpp-csv-parser/* \
     #                     */lib/autom4te.cache/* \
     #                     */lib/build/* \
     #                     */lib/cmake-*/* \
     #                     */lib/Debug/* \
     #                     */lib/m4/* \
     #                     */lib/Makefiles/* \
     #                     */lib/obj/* \
     #                     */lib/Release/* \
     #                     */lib/SimTest/* \
     #                     *.d \
     #                     *CMakeLists.txt\
     #                     */LICENSE.txt
	# EXCLUDE                = ../pycoalescence/lib/necsim/fast-cpp-csv-parser \
     #                     necsim/fast-cpp-csv-parser/ \
     #                     ../../necsim/fast-cpp-csv-parser/
	# '''
}


# Breathe compatibility
def setup(app):
	pass
	# with open("README_NECSim.rst", mode="r") as readme:
	# 	data = readme.read()
	# stripPath = "../PyCoalescence/NECSim/Documentation/"
	# generateDoxygenXML(stripPath)
	# exhaleArgs = {
	# 	"doxygenIndexXMLPath": "../PyCoalescence/NECSim/Documentation/xml/index.xml",
	# 	"containmentFolder": "./Exhaled",
	# 	"rootFileName": "exhaled_library.rst",
	# 	"rootFileTitle": "NECSim",
	# 	"doxygenStripFromPath": stripPath,
	# 	"afterTitleDescription": data,
	# 	"createTreeView": True,
	# 	"exhaleExecutesDoxygen": True,
	# 	"exhaleDoxygenStdin": "INPUT = ../PyCoalescence/NECSim"}
	# create the dictionary to send to exhale



	# import the exhale module from the current directory and generate the necsim
	# sys.path.insert(0, os.path.abspath('.'))  # exhale.py is in this directory
	# from exhale import generate
	# generate(exhaleArgs)
