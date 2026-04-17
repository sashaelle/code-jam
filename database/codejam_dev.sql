--
-- PostgreSQL database dump
--

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-09 10:53:34

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

--
-- TOC entry 2 (class 3079 OID 24744)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5082 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 24782)
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    account_id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(10) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT accounts_role_check CHECK (((role)::text = ANY ((ARRAY['team'::character varying, 'judge'::character varying, 'admin'::character varying])::text[])))
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 24820)
-- Name: judges; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.judges (
    judge_id integer NOT NULL,
    account_id uuid NOT NULL,
    display_name character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.judges OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24819)
-- Name: judges_judge_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.judges ALTER COLUMN judge_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.judges_judge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 222 (class 1259 OID 24800)
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    team_id integer NOT NULL,
    account_id uuid NOT NULL,
    team_number character varying(20),
    team_name character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24799)
-- Name: teams_team_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.teams ALTER COLUMN team_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.teams_team_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 5072 (class 0 OID 24782)
-- Dependencies: 220
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (account_id, username, password_hash, role, is_active, created_at) FROM stdin;
06f3bd78-b88c-4c2c-9d19-3114023de1a1	admin_test	hash	admin	t	2026-04-08 11:21:55.795204
1b934f24-0dc0-48c3-be10-a2e9efb64e85	judge	codejamjudge	judge	t	2026-04-08 11:41:13.481365
93c64e76-f579-488a-8b59-b9be4d773c02	admin	codejamadmin	admin	t	2026-04-08 11:41:13.481365
36b43eb0-916c-4063-8212-be09f1fea8bd	Team1	codejamteam	team	t	2026-04-08 11:41:13.481365
\.


--
-- TOC entry 5076 (class 0 OID 24820)
-- Dependencies: 224
-- Data for Name: judges; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.judges (judge_id, account_id, display_name, created_at) FROM stdin;
1	1b934f24-0dc0-48c3-be10-a2e9efb64e85	Judge 1	2026-04-08 11:44:05.573549
\.


--
-- TOC entry 5074 (class 0 OID 24800)
-- Dependencies: 222
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teams (team_id, account_id, team_number, team_name, created_at) FROM stdin;
1	36b43eb0-916c-4063-8212-be09f1fea8bd	team_1	Team 1	2026-04-08 11:43:03.373876
\.


--
-- TOC entry 5083 (class 0 OID 0)
-- Dependencies: 223
-- Name: judges_judge_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.judges_judge_id_seq', 1, true);


--
-- TOC entry 5084 (class 0 OID 0)
-- Dependencies: 221
-- Name: teams_team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teams_team_id_seq', 1, true);


--
-- TOC entry 4910 (class 2606 OID 24796)
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (account_id);


--
-- TOC entry 4912 (class 2606 OID 24798)
-- Name: accounts accounts_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_username_key UNIQUE (username);


--
-- TOC entry 4920 (class 2606 OID 24831)
-- Name: judges judges_account_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judges
    ADD CONSTRAINT judges_account_id_key UNIQUE (account_id);


--
-- TOC entry 4922 (class 2606 OID 24829)
-- Name: judges judges_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judges
    ADD CONSTRAINT judges_pkey PRIMARY KEY (judge_id);


--
-- TOC entry 4914 (class 2606 OID 24811)
-- Name: teams teams_account_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_account_id_key UNIQUE (account_id);


--
-- TOC entry 4916 (class 2606 OID 24809)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 4918 (class 2606 OID 24813)
-- Name: teams teams_team_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_team_number_key UNIQUE (team_number);


--
-- TOC entry 4924 (class 2606 OID 24832)
-- Name: judges fk_judges_account; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judges
    ADD CONSTRAINT fk_judges_account FOREIGN KEY (account_id) REFERENCES public.accounts(account_id) ON DELETE CASCADE;


--
-- TOC entry 4923 (class 2606 OID 24814)
-- Name: teams fk_teams_account; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_teams_account FOREIGN KEY (account_id) REFERENCES public.accounts(account_id) ON DELETE CASCADE;


-- Completed on 2026-04-09 10:53:36

--
-- PostgreSQL database dump complete
--


