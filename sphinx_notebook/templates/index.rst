===================
My Notebook
===================

{% set headers = (
    '',
    '========================================',
    '----------------------------------------',
    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    )
%}

{% macro dump_children(children) -%}
{%- endmacro %}

{% for node in nodes -%}

{% if not node.is_leaf %}
{{ node.name }}
{{ headers[node.depth] }}

{% if node.children | selectattr("is_leaf") | list | count -%}
.. list-table::

{% for row in node.children | selectattr("is_leaf") | batch(4) -%}
{% for col in row -%}
{% if loop.first %}
{{ "\t * - :ref:`%s <%s>"|format(col.title, col.ref_id)}}
{% else %}
{{ "\t   - :ref:`%s <%s>"|format(col.title, col.ref_id)}}
{% endif %}
{% endfor %}

{% endfor %}

{% endif %}
{% endif %}

{%- endfor %}
