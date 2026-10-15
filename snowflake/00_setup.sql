-- One-off Snowflake setup. Run it in a Snowsight worksheet.
use role accountadmin;

-- Compute: smallest warehouse, pauses itself after 60 s idle
create warehouse if not exists tpch_wh
    warehouse_size = 'XSMALL' auto_suspend = 60 auto_resume = true initially_suspended = true;

-- Storage: our own database (dbt creates the BRONZE / SILVER / GOLD schemas inside it)
create database if not exists tpch_medallion;

-- Role used by dbt; granted to SYSADMIN so you can browse the results in Snowsight
create role if not exists transformer;
grant role transformer to role sysadmin;
grant usage on warehouse tpch_wh to role transformer;
grant all on database tpch_medallion to role transformer;
grant imported privileges on database snowflake_sample_data to role transformer;

-- User for dbt. Snowflake no longer accepts password-only logins, so it uses a key pair.
create user if not exists dbt_user
    type = service
    default_role = transformer
    default_warehouse = tpch_wh
    rsa_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiMSKbsEbSMHHTdZnYI+aN1NGK3sAdcaM6DcER7KA0+3Z2F6pCURBu3JUz8x9nennDqJjEZL3rgpxdFHo+ehKHVi3xeTLBDTAgjjh3yyAg55MDcqe9VF38EVGkYYihcRCTYS0+i+Qim+hMrJUeu89hDn7SQLgL8WizZTahWFJduZ3yN4R35xsc7I9PnwRXAQZlUTzTws+z8o/NvhEXoQnco5jFVQPGR62WQt+Sdb1zw8XkkPeESwDVnu+cU7tg4uwB5RIty7E5dprmURXnTyzTK3ih3jwQToFjXgu3BmuvEMfvJ7Je5gD7ZENIyKnYhBfKgwUUy57HEfoyCjSUBTkcwIDAQAB';
grant role transformer to user dbt_user;
