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

{% endif %}

{%- endfor %}
