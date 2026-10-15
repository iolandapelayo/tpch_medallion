{# Custom generic tests. A test passes when its query returns zero rows. #}

{# Values must be >= min_value and, if given, <= max_value. #}
{% test value_between(model, column_name, min_value, max_value=none) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} < {{ min_value }}
{%- if max_value is not none %}
   or {{ column_name }} > {{ max_value }}
{%- endif %}
{% endtest %}


{# The combination of columns must be unique (composite primary key). #}
{% test unique_combination(model, combination_of_columns) %}
select {{ combination_of_columns | join(', ') }}
from {{ model }}
group by {{ combination_of_columns | join(', ') }}
having count(*) > 1
{% endtest %}
