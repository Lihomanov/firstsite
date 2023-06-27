
CREATE TABLE User
(
    user_id   serial primary key,
    last_name varchar(100) not null,
    role      varchar(30)  not null,
    username  varchar(100) not null,
    phone     varchar(100) not null
);

CREATE TABLE Discount
(
    discount_id   serial primary key,
    discount_name varchar(30)  not null,
    description   varchar(200) not null,
    start_date    date         not null,
    end_date      date         not null
);

CREATE TABLE Smartphone
(
    name_smartphone serial primary key,
    model           varchar(30) not null,
    name_company    varchar(30) not null,
    color           varchar(30) not null,
    os              varchar(20) not null,
    price           integer     not null
);

CREATE TABLE Warehouse
(
    warehouse_id serial primary key,
    address      varchar(100) not null,
    area         integer      not null
);

CREATE TABLE Status
(
    status_id   serial primary key,
    name_status varchar(50)  not null,
    description varchar(100) not null
);

CREATE TABLE Orders
(
    order_id     serial primary key,
    id_model     integer     not null references Smartphone (name_smartphone) on update cascade on delete cascade,
    id_user      integer     not null references User (user_id) on update cascade on delete cascade,
    order_date   date        not null,
    payment_form varchar(50) not null,
    address_id   integer     not null references Warehouse (warehouse_id) on update cascade on delete cascade,
    id_status    integer     not null references Status (status_id) on update cascade on delete cascade,
    id_discount  integer     not null references Discount (discount_id) on update cascade on delete cascade,
    price integer not null,
    rating integer not null,
    id_reviews varchar(200) not null
);


SELECT Smartphone.model,
       Smartphone.name_company,
       Orders.order_date,
       Orders.payment_form,
       Warehouse.address,
       Status.name_status,
       Discount.discount_name,
       Orders.price,
       Orders.rating,
       Orders.id_reviews
from Orders
         inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
         inner join Warehouse on Orders.id_discount = Warehouse.warehouse_id
         inner join Discount on Orders.id_discount = Discount.discount_id
         inner join Status on Orders.id_status = Status.status_id