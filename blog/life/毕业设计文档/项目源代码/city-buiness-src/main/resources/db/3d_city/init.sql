create table if not exists users
(
    id            bigint auto_increment
        primary key,
    created_at    datetime(6) default CURRENT_TIMESTAMP(6) not null,
    email         varchar(128)                             not null,
    password_hash varchar(255)                             not null,
    status        int         default 1                    not null,
    updated_at    datetime(6) default CURRENT_TIMESTAMP(6) not null,
    username      varchar(64)                              not null,
    constraint email
        unique (email),
    constraint username
        unique (username)
);

create table if not exists jobs
(
    id           bigint auto_increment
        primary key,
    created_at   datetime(6) default CURRENT_TIMESTAMP(6) not null,
    payload_json json                                     not null,
    result_json  json                                     null,
    status       int         default 0                    not null,
    type         tinytext                                 not null,
    updated_at   datetime(6) default CURRENT_TIMESTAMP(6) not null,
    user_id      bigint                                   not null,
    task_id      varchar(64)                              not null comment '任务唯一ID',
    layout_id    bigint                                   null comment '布局ID',
    constraint idx_task_id
        unique (task_id),
    constraint task_id
        unique (task_id),
    constraint FKra3g6pshf0p0hv5aisuh3weg8
        foreign key (user_id) references users (id)
            on delete cascade
);

create index idx_created_at
    on jobs (created_at);

create index idx_layout_id
    on jobs (layout_id);

create index idx_status
    on jobs (status);

create index idx_user_id
    on jobs (user_id);

create table if not exists layouts
(
    id          bigint auto_increment
        primary key,
    created_at  datetime(6) default CURRENT_TIMESTAMP(6) not null,
    params_json json                                     not null,
    status      int         default 0                    not null,
    svg_hash    varchar(128)                             not null,
    svg_url     varchar(512)                             not null,
    updated_at  datetime(6) default CURRENT_TIMESTAMP(6) not null,
    user_id     bigint                                   not null,
    constraint FK5n2lbrgss5jkbrfxwbyj833ts
        foreign key (user_id) references users (id)
            on delete cascade
);

create index idx_created_at
    on layouts (created_at);

create index idx_status
    on layouts (status);

create index idx_svg_hash
    on layouts (svg_hash);

create index idx_user_id
    on layouts (user_id);

create table if not exists models
(
    id         bigint auto_increment
        primary key,
    created_at datetime(6) default CURRENT_TIMESTAMP(6) not null,
    mtl_url    varchar(512)                             not null,
    obj_url    varchar(512)                             not null,
    status     int         default 0                    not null,
    updated_at datetime(6) default CURRENT_TIMESTAMP(6) not null,
    layout_id  bigint                                   not null,
    user_id    bigint                                   not null,
    constraint FKq4wl824fydrrrx9y0solk7b6o
        foreign key (layout_id) references layouts (id)
            on delete cascade,
    constraint FKswk3uvrv4o3sabjd3y7mhafv8
        foreign key (user_id) references users (id)
            on delete cascade
);

create index idx_created_at
    on models (created_at);

create index idx_layout_id
    on models (layout_id);

create index idx_status
    on models (status);

create index idx_user_id
    on models (user_id);

create table if not exists sessions
(
    id         bigint auto_increment
        primary key,
    created_at datetime(6) default CURRENT_TIMESTAMP(6) not null,
    expires_at datetime(6)                              null,
    token      varchar(255)                             not null,
    user_id    bigint                                   not null,
    constraint token
        unique (token),
    constraint FKruie73rneumyyd1bgo6qw8vjt
        foreign key (user_id) references users (id)
            on delete cascade
);

create index idx_expires_at
    on sessions (expires_at);

create index idx_token
    on sessions (token);

create index idx_user_id
    on sessions (user_id);

create index idx_created_at
    on users (created_at);

create index idx_email
    on users (email);

create index idx_status
    on users (status);

create index idx_username
    on users (username);

