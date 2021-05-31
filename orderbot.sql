--
-- PostgreSQL database dump
--

-- Dumped from database version 10.14
-- Dumped by pg_dump version 13.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO pgroot;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    user_id integer NOT NULL,
    phone character varying(15),
    body text,
    created_at timestamp without time zone
);


ALTER TABLE public.messages OWNER TO pgroot;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: pgroot
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO pgroot;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgroot
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: user_api_companies; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.user_api_companies (
    id integer NOT NULL,
    comapny_name character varying(256)
);


ALTER TABLE public.user_api_companies OWNER TO pgroot;

--
-- Name: user_api_companies_id_seq; Type: SEQUENCE; Schema: public; Owner: pgroot
--

CREATE SEQUENCE public.user_api_companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_api_companies_id_seq OWNER TO pgroot;

--
-- Name: user_api_companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgroot
--

ALTER SEQUENCE public.user_api_companies_id_seq OWNED BY public.user_api_companies.id;


--
-- Name: user_api_details; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.user_api_details (
    id integer NOT NULL,
    user_id integer NOT NULL,
    key character varying(256),
    host character varying(256),
    username character varying(256),
    password character varying(256),
    api_company_id integer
);


ALTER TABLE public.user_api_details OWNER TO pgroot;

--
-- Name: user_api_details_id_seq; Type: SEQUENCE; Schema: public; Owner: pgroot
--

CREATE SEQUENCE public.user_api_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_api_details_id_seq OWNER TO pgroot;

--
-- Name: user_api_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgroot
--

ALTER SEQUENCE public.user_api_details_id_seq OWNED BY public.user_api_details.id;


--
-- Name: user_api_urls; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.user_api_urls (
    id integer NOT NULL,
    user_id integer NOT NULL,
    api_name character varying(256),
    method character varying(10),
    requirement_header text,
    requirement_body text,
    requirement_response text
);


ALTER TABLE public.user_api_urls OWNER TO pgroot;

--
-- Name: user_api_urls_id_seq; Type: SEQUENCE; Schema: public; Owner: pgroot
--

CREATE SEQUENCE public.user_api_urls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_api_urls_id_seq OWNER TO pgroot;

--
-- Name: user_api_urls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgroot
--

ALTER SEQUENCE public.user_api_urls_id_seq OWNED BY public.user_api_urls.id;


--
-- Name: user_catalogues; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.user_catalogues (
    id integer NOT NULL,
    user_id integer NOT NULL,
    property_id integer,
    property_name character varying(256),
    catalogue_image character varying(256),
    price character varying(20),
    currency character varying(20),
    id_ru integer,
    link text
);


ALTER TABLE public.user_catalogues OWNER TO pgroot;

--
-- Name: user_catalogues_id_seq; Type: SEQUENCE; Schema: public; Owner: pgroot
--

CREATE SEQUENCE public.user_catalogues_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_catalogues_id_seq OWNER TO pgroot;

--
-- Name: user_catalogues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgroot
--

ALTER SEQUENCE public.user_catalogues_id_seq OWNED BY public.user_catalogues.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: pgroot
--

CREATE TABLE public.users (
    id integer NOT NULL,
    phone_number character varying(12),
    phone_number_encrypted character varying(256),
    password character varying(256),
    email character varying(256) NOT NULL,
    hook text NOT NULL,
    welcome_msg text,
    type_of_business integer DEFAULT 1 NOT NULL,
    created_at timestamp without time zone,
    bot_token text
);


ALTER TABLE public.users OWNER TO pgroot;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: pgroot
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO pgroot;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgroot
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: user_api_companies id; Type: DEFAULT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_companies ALTER COLUMN id SET DEFAULT nextval('public.user_api_companies_id_seq'::regclass);


--
-- Name: user_api_details id; Type: DEFAULT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_details ALTER COLUMN id SET DEFAULT nextval('public.user_api_details_id_seq'::regclass);


--
-- Name: user_api_urls id; Type: DEFAULT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_urls ALTER COLUMN id SET DEFAULT nextval('public.user_api_urls_id_seq'::regclass);


--
-- Name: user_catalogues id; Type: DEFAULT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_catalogues ALTER COLUMN id SET DEFAULT nextval('public.user_catalogues_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: pgroot
--

INSERT INTO public.alembic_version (version_num) VALUES ('b5fbb12d6994');
INSERT INTO public.alembic_version (version_num) VALUES ('ea2ac3f2dfda');


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: pgroot
--

INSERT INTO public.messages (id, user_id, phone, body, created_at) VALUES (1, 1, '1234567890', 'this is test msg', '2021-01-10 04:17:47.375897');


--
-- Data for Name: user_api_companies; Type: TABLE DATA; Schema: public; Owner: pgroot
--

INSERT INTO public.user_api_companies (id, comapny_name) VALUES (1, 'holigest');


--
-- Data for Name: user_api_details; Type: TABLE DATA; Schema: public; Owner: pgroot
--

INSERT INTO public.user_api_details (id, user_id, key, host, username, password, api_company_id) VALUES (1, 1, 'testapikey', 'https://hiresicily.holigest.it/', 'GioApi', 'ARP_x5_21-@', 1);
INSERT INTO public.user_api_details (id, user_id, key, host, username, password, api_company_id) VALUES (4, 2, 'testapikey', 'https://hiresicily.holigest.it/', 'GioApi', 'ARP_x5_21-@', 1);


--
-- Data for Name: user_api_urls; Type: TABLE DATA; Schema: public; Owner: pgroot
--



--
-- Data for Name: user_catalogues; Type: TABLE DATA; Schema: public; Owner: pgroot
--

INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (13, 1, 7, 'Apt B - Wellness House Galilei 3 sleeps', 'hiresicily_10.jpg', '42', 'EUR', 1691658, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-3-sleeps---apt-b----7');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (7, 1, 9, 'Apt D - Wellnes House Galilei 6 sleeps ', 'hiresicily_4.jpg', '74', 'EUR', 1691660, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-6-sleeps---apt-d-9');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (12, 1, 6, 'Apt A - Wellness House Galilei 5 sleeps', 'hiresicily_9.jpg', '55', 'EUR', 1691657, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-galilei-apt-a---5-sleeps-6');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (3, 1, 10, 'Apt F - Wellness House Galilei 14 Sleeps', 'hiresicily_1.jpg', '84', 'EUR', 1691662, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-14-sleeps---apt-f----10');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (5, 1, 8, 'Apt C - Wellness Hose Galilei 8 sleeps', 'hiresicily_3.jpg', '136', 'EUR', 1691659, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-8-sleeps---apt-c----8');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (4, 1, 5, 'Giardino Tropicale Eco-friendly accomodation, wide tropical garden, by the sea', 'hiresicily_2.jpg', '122', 'EUR', 2165412, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/giardino-tropicale---350-mt-from-beach-wide-garden-5');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (8, 1, 2, 'Apt E - Wellness Hose Galilei 9 sleeps', 'hiresicily_5.jpg', '94', 'EUR', 1115731, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-9-sleeps---apt-e----2');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (9, 1, 4, 'Giardino di Limoni Eco friendly Villa close to the beach', 'hiresicily_6.jpg', '245', 'EUR', 1144860, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/villa-giardino-di-limoni-4');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (10, 1, 3, 'Casale della Pergola Eco friendly firm house by the sea ', 'hiresicily_7.jpg', '122', 'EUR', 1144798, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/casale-della-pergola-3');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (11, 1, 1, 'Apartment Eucaliptus sea view terrace, 40 mt from sea', 'hiresicily_8.jpg', '88', 'EUR', 1132672, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/apartment-eucaliptus-sea-view-forty-mt-from-beach-1');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (14, 2, 7, 'Apt B - Wellness House Galilei 3 sleeps', 'hiresicily_10.jpg', '42', 'EUR', 1691658, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-3-sleeps---apt-b----7');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (15, 2, 9, 'Apt D - Wellnes House Galilei 6 sleeps ', 'hiresicily_4.jpg', '74', 'EUR', 1691660, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-6-sleeps---apt-d-9');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (16, 2, 6, 'Apt A - Wellness House Galilei 5 sleeps', 'hiresicily_9.jpg', '55', 'EUR', 1691657, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-galilei-apt-a---5-sleeps-6');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (17, 2, 10, 'Apt F - Wellness House Galilei 14 Sleeps', 'hiresicily_1.jpg', '84', 'EUR', 1691662, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-14-sleeps---apt-f----10');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (18, 2, 8, 'Apt C - Wellness Hose Galilei 8 sleeps', 'hiresicily_3.jpg', '136', 'EUR', 1691659, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-8-sleeps---apt-c----8');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (19, 2, 5, 'Giardino Tropicale Eco-friendly accomodation, wide tropical garden, by the sea', 'hiresicily_2.jpg', '122', 'EUR', 2165412, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/giardino-tropicale---350-mt-from-beach-wide-garden-5');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (20, 2, 2, 'Apt E - Wellness Hose Galilei 9 sleeps', 'hiresicily_5.jpg', '94', 'EUR', 1115731, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-9-sleeps---apt-e----2');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (21, 2, 4, 'Giardino di Limoni Eco friendly Villa close to the beach', 'hiresicily_6.jpg', '245', 'EUR', 1144860, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/villa-giardino-di-limoni-4');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (22, 2, 3, 'Casale della Pergola Eco friendly firm house by the sea ', 'hiresicily_7.jpg', '122', 'EUR', 1144798, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/casale-della-pergola-3');
INSERT INTO public.user_catalogues (id, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link) VALUES (23, 2, 1, 'Apartment Eucaliptus sea view terrace, 40 mt from sea', 'hiresicily_8.jpg', '88', 'EUR', 1132672, 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/apartment-eucaliptus-sea-view-forty-mt-from-beach-1');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: pgroot
--

INSERT INTO public.users (id, phone_number, phone_number_encrypted, password, email, hook, welcome_msg, type_of_business, created_at, bot_token) VALUES (1, '917893273022', '37470c9583a8de5932b3f944391edb54', 'pbkdf2:sha256:150000$Ebq5J1k4$c97e3913ee150ee82a34b595575386778e426c621e62f068d70698585de436e6', 'dhiraj.patra@gmail.com', 'https://api.telegram.org/bot1660459333:AAExGtt2PBiWHX0qfE_-KfoNIp6Cklq7ibo/setWebhook?url=https://bizhive.tk/api/v1/telegram_hook/37470c9583a8de5932b3f944391edb54', 'Hi welcome to HOLIDAY HOMES AND VILLAS IN MARINA DI NOTO, SICILY.\nRelevant Accommodations\nDiscover our accommodations in Marina di Noto (Syracuse), near the sea\n\nHow can I help you?', 1, '2021-01-09 13:01:59.509589', '1616238596:AAFvtdMGyHVBGEWb_omiuB0D0QGCVCUS5w0');
INSERT INTO public.users (id, phone_number, phone_number_encrypted, password, email, hook, welcome_msg, type_of_business, created_at, bot_token) VALUES (2, '393387138087', 'cee161a702c664752a810eae79642bcc', 'pbkdf2:sha256:150000$I1OOOwsN$4da2092b9cce549e9570e77e70d619dd2f39b976a8ebca4a0430f140c739c971', 'gioacchino.trapani@gmail.com', 'https://api.telegram.org/bot1682360047:AAH3ComLJF8uSb5jCYeXAgySYShIwbBElxI/setWebhook?url=https://bizhive.tk/api/v1/telegram_hook/cee161a702c664752a810eae79642bcc', 'Hi welcome to HOLIDAY HOMES AND VILLAS IN MARINA DI NOTO, SICILY.
Relevant Accommodations
Discover our accommodations in Marina di Noto (Syracuse), near the sea

How can I help you?', 1, '2021-03-08 14:07:44.455938', '1682360047:AAH3ComLJF8uSb5jCYeXAgySYShIwbBElxI');


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgroot
--

SELECT pg_catalog.setval('public.messages_id_seq', 1, false);


--
-- Name: user_api_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgroot
--

SELECT pg_catalog.setval('public.user_api_companies_id_seq', 1, false);


--
-- Name: user_api_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgroot
--

SELECT pg_catalog.setval('public.user_api_details_id_seq', 4, true);


--
-- Name: user_api_urls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgroot
--

SELECT pg_catalog.setval('public.user_api_urls_id_seq', 1, false);


--
-- Name: user_catalogues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgroot
--

SELECT pg_catalog.setval('public.user_catalogues_id_seq', 4, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgroot
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: user_api_companies user_api_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_companies
    ADD CONSTRAINT user_api_companies_pkey PRIMARY KEY (id);


--
-- Name: user_api_urls user_api_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_urls
    ADD CONSTRAINT user_api_urls_pkey PRIMARY KEY (id);


--
-- Name: user_catalogues user_catalogues_pkey; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_catalogues
    ADD CONSTRAINT user_catalogues_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_hook_key; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_hook_key UNIQUE (hook);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_api_details user_api_details_api_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_details
    ADD CONSTRAINT user_api_details_api_company_id_fkey FOREIGN KEY (api_company_id) REFERENCES public.user_api_companies(id);


--
-- Name: user_api_details user_api_details_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_details
    ADD CONSTRAINT user_api_details_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_api_urls user_api_urls_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_api_urls
    ADD CONSTRAINT user_api_urls_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_catalogues user_catalogues_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pgroot
--

ALTER TABLE ONLY public.user_catalogues
    ADD CONSTRAINT user_catalogues_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

