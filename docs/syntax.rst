Gelatin Syntax
==============

The following functions and types may be used within a Gelatin syntax.

Types
-----

STRING
^^^^^^

A string is any series of characters, delimited by the :code:`'` character.
Escaping is done using the backslash character. Examples:

::

    'test me'
    'test \'escaped\' strings'

VARNAME
^^^^^^^

VARNAMEs are variable names. They may contain the following set of
characters::

    [a-z0-9_]

NODE
^^^^

The output that is generated by Gelatin is represented by a tree
consisting of nodes. The NODE type is used to describe a single node in
a tree. It is a URL notated string consisting of the node name,
optionally followed by attributes. Examples for NODE include:

::

    .
    element
    element?attribute1="foo"
    element?attribute1="foo"&attribute2="foo"

PATH
^^^^

A PATH addresses a node in the tree. Addressing is relative to the
currently selected node. A PATH is a string with the following syntax::

    NODE[/NODE[/NODE]...]'

Examples::

    .
    ./child
    parent/element?attribute="foo"
    parent/child1?name="foo"/child?attribute="foobar"

REGEX
^^^^^

This type describes a Python regular expression. The expression MUST NOT
extract any subgroups. In other words, when using bracket expressions,
always use ``(?:)``. Example::

    /^(test|foo|bar)$/         # invalid!
    /^(?:test|foo|bar)$/       # valid

If you are trying to extract a substring, use a match statement with
multiple fields instead.

Statements
----------

define VARNAME STRING|REGEX|VARNAME
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`define` statements assign a value to a variable. Examples::

    define my_test /(?:foo|bar)/
    define my_test2 'foobar'
    define my_test3 my_test2

match STRING|REGEX|VARNAME ...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Match statements are lists of tokens that are applied against the
current input document. They parse the input stream by matching at the
current position. On a match, the matching string is consumed from the
input such that the next match statement may be applied. In other words,
the current position in the document is advanced only when a match is
found.

A match statement must be followed by an indented block. In this block,
each matching token may be accessed using the `$X` variables, where `X` is
the number of the match, starting with `$0`.

Examples::

    define digit /[0-9]/
    define number /[0-9]+/

    grammar input:
        match 'foobar':
            do.say('Match was: $0!')
        match 'foo' 'bar' /[\r\n]/:
            do.say('Match was: $0!')
        match 'foobar' digit /\s+/ number /[\r\n]/:
            do.say('Matches: $1 and $3')

You may also use multiple matches resulting in a logical OR:

::

    match 'foo' '[0-9]' /[\r\n]/
        | 'bar' /[a-z]/ /[\r\n]/
        | 'foobar' /[A-Z]/ /[\r\n]/:
        do.say('Match was: $1!')

imatch STRING|REGEX|VARNAME ...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`imatch` statements are like `match` statements, except that matching is
case-insensitive.

when STRING|REGEX|VARNAME ...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`when` statements are like `match` statements, with the difference
that upon a match, the string is not consumed from the input stream.
In other words, the current position in the document is not advanced,
even when a match is found.
`when` statements are generally used in places where you want to "bail
out" of a grammar without consuming the token.

Example::

    grammar user:
        match 'Name:' /\s+/ /\S+/ /\n/:
            do.say('Name was: $2!')
        when 'User:':
            do.return()

    grammar input:
        match 'User:' /\s+/ /\S+/ /\n/:
            out.enter('user/name', '$2')
            user()

Output Generating Functions
---------------------------

out.create(PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^^^

Creates the leaf node (and attributes) in the given path, regardless
of whether or not it already exists. In other words, using this
function twice will lead to duplicates.
If the given path contains multiple elements, the parent nodes are
only created if the do not yet exist.
If the STRING argument is given, the new node is also assigned the
string as data. In other words, the following function call::

    out.create('parent/child?name="test"', 'hello world')

leads to the following XML output::

    <parent>
        <child name="test">hello world</child>
    </parent>

Using the same call again, like so::

    out.create('parent/child?name="test"', 'hello world')
    out.create('parent/child?name="test"', 'hello world')

the resulting XML would look like this::

    <parent>
        <child name="test">hello world</child>
        <child name="test">hello world</child>
    </parent>

out.replace(PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Like out.create(), but replaces the nodes in the given path if they
already exist.

out.add(PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^

Like out.create(), but appends the string to the text of the existing
node if it already exists.

out.add_attribute(PATH, NAME, STRING)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adds the attribute with the given name and value to the node with the
given path.

out.open(PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^

Like out.create(), but also selects the addressed node, such that the
PATH of all subsequent function calls is relative to the selected node
until the end of the match block is reached.

out.enter(PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^^

Like out.open(), but only creates the nodes in the given path if they do
not already exist.

out.enqueue_before(REGEX, PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Like out.add(), but is not immediately executed. Instead, it is executed
as soon as the given regular expression matches the input, regardless of
the grammar in which the match occurs.

out.enqueue_after(REGEX, PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Like out.enqueue_before(), but is executed after the given regular
expression matches the input and the next match statement was processed.

out.enqueue_on_add(REGEX, PATH[, STRING])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Like out.enqueue_before(), but is executed after the given regular
expression matches the input and the next node is added to the output.

out.clear_queue()
^^^^^^^^^^^^^^^^^

Removes any items from the queue that were previously queued using the
out.enqueue_*() functions.

Control Functions
-----------------

do.skip()
^^^^^^^^^

Skip the current match and jump back to the top of the current grammar
block.

do.next()
^^^^^^^^^

| Skip the current match and continue with the next match statement
  without jumping back to the top of the current grammar block.
| This function is rarely used and probably not what you want. Instead,
  use do.skip() in almost all cases, unless it is for some
  performance-specific hacks.

do.return()
^^^^^^^^^^^

Immediately leave the current grammar block and return to the calling
function. When used at the top level (i.e. in the `input` grammar), stop
parsing.

do.say(STRING)
^^^^^^^^^^^^^^

Prints the given string to stdout, with additional debug information.

do.fail(STRING)
^^^^^^^^^^^^^^^

Like do.say(), but immediately terminates with an error.
