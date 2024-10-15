--
-- botQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1)

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

SET default_table_access_method = heap;

--
-- Name: email; Type: TABLE; Schema: public; Owner: bot
--

-- CREATE USER bot WITH PASSWORD '123' SUPERUSER;
-- ALTER TABLE bot OWNER TO bot;
CREATE TABLE public.email (
    id integer NOT NULL,
    email character varying(70)
);


ALTER TABLE public.email OWNER TO bot;

--
-- Name: email_id_seq; Type: SEQUENCE; Schema: public; Owner: bot
--

CREATE SEQUENCE public.email_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.email_id_seq OWNER TO bot;

--
-- Name: email_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bot
--

ALTER SEQUENCE public.email_id_seq OWNED BY public.email.id;


--
-- Name: phone; Type: TABLE; Schema: public; Owner: bot
--

CREATE TABLE public.phone (
    id integer NOT NULL,
    phone_number character varying(50)
);


ALTER TABLE public.phone OWNER TO bot;

--
-- Name: phone_id_seq; Type: SEQUENCE; Schema: public; Owner: bot
--

CREATE SEQUENCE public.phone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.phone_id_seq OWNER TO bot;

--
-- Name: phone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bot
--

ALTER SEQUENCE public.phone_id_seq OWNED BY public.phone.id;


--
-- Name: email id; Type: DEFAULT; Schema: public; Owner: bot
--

ALTER TABLE ONLY public.email ALTER COLUMN id SET DEFAULT nextval('public.email_id_seq'::regclass);


--
-- Name: phone id; Type: DEFAULT; Schema: public; Owner: bot
--

ALTER TABLE ONLY public.phone ALTER COLUMN id SET DEFAULT nextval('public.phone_id_seq'::regclass);


--
-- Data for Name: email; Type: TABLE DATA; Schema: public; Owner: bot
--

COPY public.email (id, email) FROM stdin;
1	alinka@mail.ru
2	test@test.test
3	oleg-kruglenko@mail.ru
4	80001112233
\.


--
-- Data for Name: phone; Type: TABLE DATA; Schema: public; Owner: bot
--

COPY public.phone (id, phone_number) FROM stdin;
1	89992221133
6	89260574673
7	oleg-kruglenko@mail.ru
8	oleg-kruglenko@mail.ru
9	89992221133
10	89992221133
11	80001112233
\.


--
-- Name: email_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bot
--

SELECT pg_catalog.setval('public.email_id_seq', 4, true);


--
-- Name: phone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bot
--

SELECT pg_catalog.setval('public.phone_id_seq', 11, true);


--
-- botQL database dump complete
--

