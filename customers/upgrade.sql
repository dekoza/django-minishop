ALTER TABLE customers_address add column "first_name" varchar(200);
ALTER TABLE customers_address add column "last_name" varchar(200);
ALTER TABLE customers_address add column "company_name" varchar(200);
ALTER TABLE customers_address add column "nip" varchar(255);
ALTER TABLE customers_address add column "is_corporate" boolean;
UPDATE customers_address SET is_corporate = False;
