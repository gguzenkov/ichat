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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO chatdb;

--
-- Name: message_attachments; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.message_attachments (
    id integer NOT NULL,
    message_id integer,
    file_path character varying,
    file_name character varying,
    file_size integer,
    file_type character varying
);


ALTER TABLE public.message_attachments OWNER TO chatdb;

--
-- Name: message_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: chatdb
--

CREATE SEQUENCE public.message_attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.message_attachments_id_seq OWNER TO chatdb;

--
-- Name: message_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chatdb
--

ALTER SEQUENCE public.message_attachments_id_seq OWNED BY public.message_attachments.id;


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
-- Name: private_message_attachments; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.private_message_attachments (
    id integer NOT NULL,
    message_id integer,
    file_path character varying,
    file_name character varying,
    file_size integer,
    file_type character varying
);


ALTER TABLE public.private_message_attachments OWNER TO chatdb;

--
-- Name: private_message_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: chatdb
--

CREATE SEQUENCE public.private_message_attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.private_message_attachments_id_seq OWNER TO chatdb;

--
-- Name: private_message_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chatdb
--

ALTER SEQUENCE public.private_message_attachments_id_seq OWNED BY public.private_message_attachments.id;


--
-- Name: private_messages; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.private_messages (
    id integer NOT NULL,
    content character varying,
    sender_id integer,
    receiver_id integer,
    created_at timestamp without time zone,
    is_read boolean
);


ALTER TABLE public.private_messages OWNER TO chatdb;

--
-- Name: private_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: chatdb
--

CREATE SEQUENCE public.private_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.private_messages_id_seq OWNER TO chatdb;

--
-- Name: private_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chatdb
--

ALTER SEQUENCE public.private_messages_id_seq OWNED BY public.private_messages.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: chatdb
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying,
    email character varying,
    hashed_password character varying,
    created_at timestamp without time zone,
    last_active timestamp without time zone,
    avatar_url character varying
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
-- Name: message_attachments id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.message_attachments ALTER COLUMN id SET DEFAULT nextval('public.message_attachments_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: private_message_attachments id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_message_attachments ALTER COLUMN id SET DEFAULT nextval('public.private_message_attachments_id_seq'::regclass);


--
-- Name: private_messages id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_messages ALTER COLUMN id SET DEFAULT nextval('public.private_messages_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.alembic_version (version_num) FROM stdin;
6d21d9122016
\.


--
-- Data for Name: message_attachments; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.message_attachments (id, message_id, file_path, file_name, file_size, file_type) FROM stdin;
6	22	/uploads/e5471803-2c3d-4637-bcfb-2a7333263f86.jpeg	monitor.jpeg	6108	image/jpeg
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.messages (id, content, created_at, user_id) FROM stdin;
1	Тест	2025-02-21 12:03:03.685648	1
2	Хеллоу	2025-02-21 09:04:51.597901	1
4	2	2025-02-24 06:51:13.563841	1
5	Тесттест	2025-02-24 06:57:00.839367	1
7	1	2025-02-24 07:20:06.195457	1
9	000	2025-02-24 07:23:48.908736	2
10	ва	2025-02-24 08:00:59.391526	2
11	@ivanov fsg	2025-02-24 13:25:33.883853	1
12	тест	2025-02-24 13:27:33.355458	1
13	124	2025-02-24 13:31:01.41093	1
14	555	2025-02-24 13:38:12.954063	1
15	😂	2025-02-24 13:47:31.139561	1
16	щзщш	2025-02-24 14:07:54.050679	1
22		2025-02-24 14:47:33.438515	1
23	🙂	2025-02-25 06:17:57.596081	1
\.


--
-- Data for Name: private_message_attachments; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.private_message_attachments (id, message_id, file_path, file_name, file_size, file_type) FROM stdin;
\.


--
-- Data for Name: private_messages; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.private_messages (id, content, sender_id, receiver_id, created_at, is_read) FROM stdin;
2	test	1	2	2025-02-24 12:43:26.048983	f
1	test	1	1	2025-02-24 12:43:00.553277	t
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: chatdb
--

COPY public.users (id, username, email, hashed_password, created_at, last_active, avatar_url) FROM stdin;
2	ivanov	ivanov@ivanov.ru	$2b$12$cIDhK60RIdZwioQ4vq0.zu./2xBUEKmgJ8JLuuJuhEAKtSGr2yCwq	2025-02-24 07:23:21.257951	2025-02-24 13:47:50.082082	\N
1	admin	guzenkov@gmail.com	$2b$12$OWb2O02M.Y2r2Q7Mb9naJ.8hMd1KZIk.fE2lD4K7IMP13GnJxvqW2	2025-02-21 09:02:48.752096	2025-02-25 06:32:02.672672	/avatars/avatar_1.png
\.


--
-- Name: message_attachments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.message_attachments_id_seq', 6, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.messages_id_seq', 23, true);


--
-- Name: private_message_attachments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.private_message_attachments_id_seq', 1, false);


--
-- Name: private_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.private_messages_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chatdb
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: message_attachments message_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.message_attachments
    ADD CONSTRAINT message_attachments_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: private_message_attachments private_message_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_message_attachments
    ADD CONSTRAINT private_message_attachments_pkey PRIMARY KEY (id);


--
-- Name: private_messages private_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_messages
    ADD CONSTRAINT private_messages_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_message_attachments_id; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE INDEX ix_message_attachments_id ON public.message_attachments USING btree (id);


--
-- Name: ix_messages_id; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE INDEX ix_messages_id ON public.messages USING btree (id);


--
-- Name: ix_private_message_attachments_id; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE INDEX ix_private_message_attachments_id ON public.private_message_attachments USING btree (id);


--
-- Name: ix_private_messages_id; Type: INDEX; Schema: public; Owner: chatdb
--

CREATE INDEX ix_private_messages_id ON public.private_messages USING btree (id);


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
-- Name: message_attachments message_attachments_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.message_attachments
    ADD CONSTRAINT message_attachments_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id) ON DELETE CASCADE;


--
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: private_message_attachments private_message_attachments_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_message_attachments
    ADD CONSTRAINT private_message_attachments_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.private_messages(id) ON DELETE CASCADE;


--
-- Name: private_messages private_messages_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_messages
    ADD CONSTRAINT private_messages_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id);


--
-- Name: private_messages private_messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chatdb
--

ALTER TABLE ONLY public.private_messages
    ADD CONSTRAINT private_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

