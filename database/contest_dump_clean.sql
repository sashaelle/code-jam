--
-- PostgreSQL database dump
--

restrict hdFiNeE86hsGECAuxEDcbD9zABYEVhpWifBToMVHR2SDx1sCMu9ruMGUHzlShDh

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

-- Started on 2026-03-16 12:50:58 EDT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 219 (class 1259 OID 16397)
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    account_id uuid NOT NULL,
    username character varying(255),
    password_hash character varying(255),
    password_salt character varying(255),
    role_account character varying(255),
    must_reset_password boolean,
    password_last_rotated_at timestamp without time zone,
    created_at timestamp without time zone,
    last_login_at timestamp without time zone,
    is_active boolean
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16426)
-- Name: contest; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contest (
    contest_id uuid NOT NULL,
    name character varying(255),
    starts_at timestamp without time zone,
    ends_at timestamp without time zone,
    scoreboard_visible boolean
);


ALTER TABLE public.contest OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16558)
-- Name: credential_issue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credential_issue (
    credential_issue_id uuid NOT NULL,
    issued_to_account_id uuid,
    issued_by_account_id uuid,
    password_hash character varying(255),
    password_salt character varying(255),
    issued_at timestamp without time zone,
    expires_at timestamp without time zone,
    used_at timestamp without time zone,
    must_reset boolean,
    revoked boolean,
    notes text
);


ALTER TABLE public.credential_issue OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16407)
-- Name: judge; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.judge (
    judge_id uuid NOT NULL,
    display_name character varying(255),
    account_id uuid
);


ALTER TABLE public.judge OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16540)
-- Name: judging; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.judging (
    judging_id uuid NOT NULL,
    submission_id uuid,
    judge_id uuid,
    started_at timestamp without time zone,
    result character varying(255),
    notes text
);


ALTER TABLE public.judging OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16432)
-- Name: problem; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.problem (
    problem_id uuid NOT NULL,
    contest_id uuid,
    code character varying(255),
    title character varying(255),
    statement_md text,
    allowed_languages character varying(255),
    base_points integer,
    is_active boolean
);


ALTER TABLE public.problem OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16511)
-- Name: registration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registration (
    registration_id uuid NOT NULL,
    contest_id uuid,
    team_id uuid,
    registered_at timestamp without time zone
);


ALTER TABLE public.registration OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16589)
-- Name: submission_testcase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.submission_testcase (
    stc_id uuid NOT NULL,
    submission_id uuid,
    test_case_id uuid,
    status character varying(255),
    runtime_ms integer,
    stderr_snip text
);


ALTER TABLE public.submission_testcase OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16483)
-- Name: submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.submissions (
    submission_id uuid NOT NULL,
    contest_id uuid,
    team_id uuid,
    problem_id uuid,
    language_code character varying(255),
    source_code text,
    recieved_at timestamp without time zone,
    judged_at timestamp without time zone,
    status character varying(255),
    judged_by uuid,
    feedback text
);


ALTER TABLE public.submissions OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16445)
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    team_id uuid NOT NULL,
    team_number character varying(255),
    team_name character varying(255),
    account_id uuid
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16576)
-- Name: test_case; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_case (
    test_case_id uuid NOT NULL,
    problem_id uuid,
    input_blob text,
    expected_output_blob text,
    timeout_ms integer,
    ordinal integer
);


ALTER TABLE public.test_case OWNER TO postgres;

--
-- TOC entry 3898 (class 0 OID 16397)
-- Dependencies: 219
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3900 (class 0 OID 16426)
-- Dependencies: 221
-- Data for Name: contest; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3906 (class 0 OID 16558)
-- Dependencies: 227
-- Data for Name: credential_issue; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3899 (class 0 OID 16407)
-- Dependencies: 220
-- Data for Name: judge; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3905 (class 0 OID 16540)
-- Dependencies: 226
-- Data for Name: judging; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3901 (class 0 OID 16432)
-- Dependencies: 222
-- Data for Name: problem; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3904 (class 0 OID 16511)
-- Dependencies: 225
-- Data for Name: registration; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3908 (class 0 OID 16589)
-- Dependencies: 229
-- Data for Name: submission_testcase; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3903 (class 0 OID 16483)
-- Dependencies: 224
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3902 (class 0 OID 16445)
-- Dependencies: 223
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3907 (class 0 OID 16576)
-- Dependencies: 228
-- Data for Name: test_case; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3710 (class 2606 OID 16404)
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (account_id);


--
-- TOC entry 3712 (class 2606 OID 16406)
-- Name: accounts accounts_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_username_key UNIQUE (username);


--
-- TOC entry 3716 (class 2606 OID 16431)
-- Name: contest contest_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contest
    ADD CONSTRAINT contest_pkey PRIMARY KEY (contest_id);


--
-- TOC entry 3730 (class 2606 OID 16565)
-- Name: credential_issue credential_issue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credential_issue
    ADD CONSTRAINT credential_issue_pkey PRIMARY KEY (credential_issue_id);


--
-- TOC entry 3714 (class 2606 OID 16412)
-- Name: judge judge_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judge
    ADD CONSTRAINT judge_pkey PRIMARY KEY (judge_id);


--
-- TOC entry 3728 (class 2606 OID 16547)
-- Name: judging judging_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judging
    ADD CONSTRAINT judging_pkey PRIMARY KEY (judging_id);


--
-- TOC entry 3718 (class 2606 OID 16439)
-- Name: problem problem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.problem
    ADD CONSTRAINT problem_pkey PRIMARY KEY (problem_id);


--
-- TOC entry 3726 (class 2606 OID 16516)
-- Name: registration registration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_pkey PRIMARY KEY (registration_id);


--
-- TOC entry 3734 (class 2606 OID 16596)
-- Name: submission_testcase submission_testcase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submission_testcase
    ADD CONSTRAINT submission_testcase_pkey PRIMARY KEY (stc_id);


--
-- TOC entry 3724 (class 2606 OID 16490)
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (submission_id);


--
-- TOC entry 3720 (class 2606 OID 16452)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 3722 (class 2606 OID 16454)
-- Name: teams teams_team_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_team_number_key UNIQUE (team_number);


--
-- TOC entry 3732 (class 2606 OID 16583)
-- Name: test_case test_case_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_case
    ADD CONSTRAINT test_case_pkey PRIMARY KEY (test_case_id);


--
-- TOC entry 3746 (class 2606 OID 16571)
-- Name: credential_issue credential_issue_issued_by_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credential_issue
    ADD CONSTRAINT credential_issue_issued_by_account_id_fkey FOREIGN KEY (issued_by_account_id) REFERENCES public.accounts(account_id);


--
-- TOC entry 3747 (class 2606 OID 16566)
-- Name: credential_issue credential_issue_issued_to_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credential_issue
    ADD CONSTRAINT credential_issue_issued_to_account_id_fkey FOREIGN KEY (issued_to_account_id) REFERENCES public.accounts(account_id);


--
-- TOC entry 3735 (class 2606 OID 16413)
-- Name: judge judge_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judge
    ADD CONSTRAINT judge_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id);


--
-- TOC entry 3744 (class 2606 OID 16553)
-- Name: judging judging_judge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judging
    ADD CONSTRAINT judging_judge_id_fkey FOREIGN KEY (judge_id) REFERENCES public.judge(judge_id);


--
-- TOC entry 3745 (class 2606 OID 16548)
-- Name: judging judging_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.judging
    ADD CONSTRAINT judging_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(submission_id);


--
-- TOC entry 3736 (class 2606 OID 16440)
-- Name: problem problem_contest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.problem
    ADD CONSTRAINT problem_contest_id_fkey FOREIGN KEY (contest_id) REFERENCES public.contest(contest_id);


--
-- TOC entry 3742 (class 2606 OID 16517)
-- Name: registration registration_contest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_contest_id_fkey FOREIGN KEY (contest_id) REFERENCES public.contest(contest_id);


--
-- TOC entry 3743 (class 2606 OID 16522)
-- Name: registration registration_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id);


--
-- TOC entry 3749 (class 2606 OID 16597)
-- Name: submission_testcase submission_testcase_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submission_testcase
    ADD CONSTRAINT submission_testcase_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(submission_id);


--
-- TOC entry 3750 (class 2606 OID 16602)
-- Name: submission_testcase submission_testcase_test_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submission_testcase
    ADD CONSTRAINT submission_testcase_test_case_id_fkey FOREIGN KEY (test_case_id) REFERENCES public.test_case(test_case_id);


--
-- TOC entry 3738 (class 2606 OID 16491)
-- Name: submissions submissions_contest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_contest_id_fkey FOREIGN KEY (contest_id) REFERENCES public.contest(contest_id);


--
-- TOC entry 3739 (class 2606 OID 16506)
-- Name: submissions submissions_judged_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_judged_by_fkey FOREIGN KEY (judged_by) REFERENCES public.judge(judge_id);


--
-- TOC entry 3740 (class 2606 OID 16501)
-- Name: submissions submissions_problem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_problem_id_fkey FOREIGN KEY (problem_id) REFERENCES public.problem(problem_id);


--
-- TOC entry 3741 (class 2606 OID 16496)
-- Name: submissions submissions_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id);


--
-- TOC entry 3737 (class 2606 OID 16455)
-- Name: teams teams_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id);


--
-- TOC entry 3748 (class 2606 OID 16584)
-- Name: test_case test_case_problem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_case
    ADD CONSTRAINT test_case_problem_id_fkey FOREIGN KEY (problem_id) REFERENCES public.problem(problem_id);


-- Completed on 2026-03-16 12:50:58 EDT

--
-- PostgreSQL database dump complete
--

