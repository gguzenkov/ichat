--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6 (Ubuntu 16.6-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.6 (Ubuntu 16.6-0ubuntu0.24.04.1)

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
-- Name: messages; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    content character varying,
    created_at timestamp without time zone,
    user_id integer
);


ALTER TABLE public.messages OWNER TO chatdb;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: chatdb
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO chatdb;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chatdb
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying,
    email character varying,
    hashed_password character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO chatdb;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: chatdb
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO chatdb;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chatdb
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.messages (id, content, created_at, user_id) FROM stdin;
1	Тест	2025-02-21 12:03:03.685648	1
2	Хеллоу	2025-02-21 09:04:51.597901	1
4	2	2025-02-24 06:51:13.563841	1
5	Тесттест	2025-02-24 06:57:00.839367	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.users (id, username, email, hashed_password, created_at) FROM stdin;
1	admin	guzenkov@gmail.com	$2b$12$OWb2O02M.Y2r2Q7Mb9naJ.8hMd1KZIk.fE2lD4K7IMP13GnJxvqW2	2025-02-21 09:02:48.752096
\.


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.messages_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_messages_id; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE INDEX ix_messages_id ON public.messages USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

