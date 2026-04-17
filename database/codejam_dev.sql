--
-- PostgreSQL database dump
--

\restrict 1EFuevz1GCBgfPL3rbaNOddcV2rWvoGd0t52yo2bgNtmOhspZcSjT0YAbLSioWj

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-17 01:10:02

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
-- TOC entry 2 (class 3079 OID 33026)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5107 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 33120)
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    account_id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 33119)
-- Name: accounts_account_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accounts_account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accounts_account_id_seq OWNER TO postgres;

--
-- TOC entry 5108 (class 0 OID 0)
-- Dependencies: 220
-- Name: accounts_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accounts_account_id_seq OWNED BY public.accounts.account_id;


--
-- TOC entry 225 (class 1259 OID 33160)
-- Name: problems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.problems (
    problem_id integer NOT NULL,
    problem_num integer NOT NULL
);


ALTER TABLE public.problems OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 33159)
-- Name: problems_problem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.problems_problem_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.problems_problem_id_seq OWNER TO postgres;

--
-- TOC entry 5109 (class 0 OID 0)
-- Dependencies: 224
-- Name: problems_problem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.problems_problem_id_seq OWNED BY public.problems.problem_id;


--
-- TOC entry 229 (class 1259 OID 33192)
-- Name: submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.submissions (
    submission_id integer NOT NULL,
    team_id integer NOT NULL,
    problem_id integer NOT NULL,
    submission_code text NOT NULL,
    judge_feedback text,
    points integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.submissions OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 33191)
-- Name: submissions_submission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.submissions_submission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.submissions_submission_id_seq OWNER TO postgres;

--
-- TOC entry 5110 (class 0 OID 0)
-- Dependencies: 228
-- Name: submissions_submission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.submissions_submission_id_seq OWNED BY public.submissions.submission_id;


--
-- TOC entry 223 (class 1259 OID 33139)
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    team_id integer NOT NULL,
    account_id integer NOT NULL,
    team_name character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT teams_creaed_at_not_null NOT NULL,
    team_number text NOT NULL
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 33138)
-- Name: teams_team_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teams_team_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teams_team_id_seq OWNER TO postgres;

--
-- TOC entry 5111 (class 0 OID 0)
-- Dependencies: 222
-- Name: teams_team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teams_team_id_seq OWNED BY public.teams.team_id;


--
-- TOC entry 227 (class 1259 OID 33171)
-- Name: test_cases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_cases (
    test_case_id integer NOT NULL,
    problem_id integer NOT NULL,
    test_case_num integer NOT NULL,
    input_text text NOT NULL,
    expected_output text NOT NULL
);


ALTER TABLE public.test_cases OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 33170)
-- Name: test_cases_test_case_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_cases_test_case_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_cases_test_case_id_seq OWNER TO postgres;

--
-- TOC entry 5112 (class 0 OID 0)
-- Dependencies: 226
-- Name: test_cases_test_case_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_cases_test_case_id_seq OWNED BY public.test_cases.test_case_id;


--
-- TOC entry 4914 (class 2604 OID 33123)
-- Name: accounts account_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts ALTER COLUMN account_id SET DEFAULT nextval('public.accounts_account_id_seq'::regclass);


--
-- TOC entry 4919 (class 2604 OID 33163)
-- Name: problems problem_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.problems ALTER COLUMN problem_id SET DEFAULT nextval('public.problems_problem_id_seq'::regclass);


--
-- TOC entry 4921 (class 2604 OID 33195)
-- Name: submissions submission_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions ALTER COLUMN submission_id SET DEFAULT nextval('public.submissions_submission_id_seq'::regclass);


--
-- TOC entry 4917 (class 2604 OID 33142)
-- Name: teams team_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams ALTER COLUMN team_id SET DEFAULT nextval('public.teams_team_id_seq'::regclass);


--
-- TOC entry 4920 (class 2604 OID 33174)
-- Name: test_cases test_case_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases ALTER COLUMN test_case_id SET DEFAULT nextval('public.test_cases_test_case_id_seq'::regclass);


--
-- TOC entry 5093 (class 0 OID 33120)
-- Dependencies: 221
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (account_id, username, password_hash, role, is_active, created_at) FROM stdin;
1	admin	codejamadmin	admin	t	2026-04-16 00:33:37.523929
21	Team1	3JiE%u8YrFM$	team	t	2026-04-16 02:12:17.927904
22	Team2	dF4QX#bvyT%L	team	t	2026-04-16 02:12:17.927904
23	Team3	8JmjtbYWV7sf	team	t	2026-04-16 02:12:17.927904
24	Team4	NVL#p3BVRurb	team	t	2026-04-16 02:12:17.927904
\.


--
-- TOC entry 5097 (class 0 OID 33160)
-- Dependencies: 225
-- Data for Name: problems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.problems (problem_id, problem_num) FROM stdin;
1	1
2	2
3	3
4	4
5	5
\.


--
-- TOC entry 5101 (class 0 OID 33192)
-- Dependencies: 229
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.submissions (submission_id, team_id, problem_id, submission_code, judge_feedback, points, "timestamp") FROM stdin;
3	14	1	code	\N	20	2026-04-16 02:16:49.887056
4	14	2	code	\N	15	2026-04-16 02:16:49.887056
5	14	3	code	\N	10	2026-04-16 02:16:49.887056
6	15	1	code	\N	20	2026-04-16 02:16:49.887056
7	15	2	code	\N	15	2026-04-16 02:16:49.887056
8	16	1	code	\N	20	2026-04-16 02:16:49.887056
\.


--
-- TOC entry 5095 (class 0 OID 33139)
-- Dependencies: 223
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teams (team_id, account_id, team_name, created_at, team_number) FROM stdin;
14	21	Team 1	2026-04-16 02:12:17.927904	team_1
15	22	Team 2	2026-04-16 02:12:17.927904	team_2
16	23	Team 3	2026-04-16 02:12:17.927904	team_3
17	24	Team 4	2026-04-16 02:12:17.927904	team_4
\.


--
-- TOC entry 5099 (class 0 OID 33171)
-- Dependencies: 227
-- Data for Name: test_cases; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.test_cases (test_case_id, problem_id, test_case_num, input_text, expected_output) FROM stdin;
5	5	1	1d4-8	-5.5
6	5	2	6d7	24.0
7	5	3	123d456+789	28894.5
\.


--
-- TOC entry 5113 (class 0 OID 0)
-- Dependencies: 220
-- Name: accounts_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_account_id_seq', 24, true);


--
-- TOC entry 5114 (class 0 OID 0)
-- Dependencies: 224
-- Name: problems_problem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.problems_problem_id_seq', 6, true);


--
-- TOC entry 5115 (class 0 OID 0)
-- Dependencies: 228
-- Name: submissions_submission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.submissions_submission_id_seq', 14, true);


--
-- TOC entry 5116 (class 0 OID 0)
-- Dependencies: 222
-- Name: teams_team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teams_team_id_seq', 25, true);


--
-- TOC entry 5117 (class 0 OID 0)
-- Dependencies: 226
-- Name: test_cases_test_case_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.test_cases_test_case_id_seq', 1, false);


--
-- TOC entry 4924 (class 2606 OID 33135)
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (account_id);


--
-- TOC entry 4926 (class 2606 OID 33137)
-- Name: accounts accounts_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_username_key UNIQUE (username);


--
-- TOC entry 4932 (class 2606 OID 33167)
-- Name: problems problems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_pkey PRIMARY KEY (problem_id);


--
-- TOC entry 4934 (class 2606 OID 33169)
-- Name: problems problems_problem_num_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_problem_num_key UNIQUE (problem_num);


--
-- TOC entry 4940 (class 2606 OID 33205)
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (submission_id);


--
-- TOC entry 4928 (class 2606 OID 33151)
-- Name: teams teams_account_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_account_id_key UNIQUE (account_id);


--
-- TOC entry 4930 (class 2606 OID 33149)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 4936 (class 2606 OID 33183)
-- Name: test_cases test_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_pkey PRIMARY KEY (test_case_id);


--
-- TOC entry 4938 (class 2606 OID 33185)
-- Name: test_cases test_cases_problem_id_test_case_num_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_problem_id_test_case_num_key UNIQUE (problem_id, test_case_num);


--
-- TOC entry 4943 (class 2606 OID 33211)
-- Name: submissions submissions_problem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_problem_id_fkey FOREIGN KEY (problem_id) REFERENCES public.problems(problem_id) ON DELETE CASCADE;


--
-- TOC entry 4944 (class 2606 OID 33206)
-- Name: submissions submissions_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 4941 (class 2606 OID 33154)
-- Name: teams teams_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id) ON DELETE CASCADE;


--
-- TOC entry 4942 (class 2606 OID 33186)
-- Name: test_cases test_cases_problem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_problem_id_fkey FOREIGN KEY (problem_id) REFERENCES public.problems(problem_id) ON DELETE CASCADE;


-- Completed on 2026-04-17 01:10:02

--
-- PostgreSQL database dump complete
--

\unrestrict 1EFuevz1GCBgfPL3rbaNOddcV2rWvoGd0t52yo2bgNtmOhspZcSjT0YAbLSioWj

