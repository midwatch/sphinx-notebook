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
{% for column in row -%}
{% if loop.first %}
{{ "\t * - %s"|format(column.title)}}
{% else %}
{{ "\t   - %s"|format(column.title)}}
{% endif %}
{% endfor %}

{% endfor %}

{% endif %}
{% endif %}

{%- endfor %}
