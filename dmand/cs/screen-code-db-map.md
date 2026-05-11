# CS 화면 → 코드 경로 · DB 테이블 매핑

> **목적:** CS/Claude Code 에이전트가 오류 제보 시 Glob 없이 `Read`할 파일과, 데이터 이슈 시 조회할 **MySQL 테이블**을 빠르게 특정한다.  
> **코드 경로**는 `deeplehr` 워크스페이스 루트 기준 (`gocho/`, `GOCHO_BE/`, `flutter-gocho-app/`). 레포 분리 시 동일 상대 경로만 맞추면 된다.

---

## 출처 · 주의

| 항목 | 출처 |
|------|------|
| **DB 테이블명** | JPA `@Table(name = "...")` — `GOCHO_BE/be/domain/src/main/java/com/demand/application/**/domain/*.java` |
| **스키마/실DB** | 운영·개발 DB는 별도. 로컬/에이전트 조회 시 `deeple-context/shared/db-guide.md` (예: DB `GD_dev`, MCP 읽기 전용) |
| **누락 가능성** | `@Table`만 인용. 매퍼/네이티브 쿼리 전용 테이블은 코드 검색으로 보완. `order`는 MySQL 예약어이므로 쿼리 시 백틱 필요할 수 있음 |

테이블 전체 목록이 필요하면 엔티티 디렉터리에서 `@Table(name` 검색하거나 `SHOW TABLES` + `db-guide.md`의 mysql-analyst 위임.

---

## 종합 매핑표

| CS 화면명 | Web (핵심 파일) | BE (핵심 파일) | App (핵심 파일) | 연관 DB 테이블 (우선순위) |
|-----------|-----------------|----------------|-----------------|---------------------------|
| 홈 | `gocho/apps/new_gocho/src/pages/index.page.tsx`, `pages/index/part/*` | `adapter/in/api/banner/controller/BannerController.java`, `application/jd/service/JdService.java` | `flutter-gocho-app/lib/feature/home/main/home_screen.dart` | `banner_statistics`, `jd`, `jd_rank` (노출/정렬) |
| 통합 검색 | `pages/search/index.page.tsx` | `keyword/controller/KeywordController.java`, `application/keyword/service/SearchKeywordService.java` | `feature/search/ui/main/search_screen.dart` | `search_keyword`, `company_keyword`, `jd` |
| JD 목록 | `pages/jd/index.page.tsx`, `jd/part/JdListPart/*` | `jd/controller/JdController.java`, `JdService.java` | `feature/jd/ui/main/jd_screen.dart`, `jd_tab_screen.dart` | `jd`, `jd_bookmark`, `user_jd_filter` |
| JD 상세 | `pages/jd/detail/[jdId].page.tsx`, `detail/part/*` | `JdController.java`, `JdService.java` | `feature/jd/ui/detail/jd_detail_screen.dart`, `jd_detail_controller.dart` | `jd`, `jd_bookmark`, `jd_view`, `jd_click`, `jd_cover_letter`, `jd_place`, `jd_place_address` |
| 회사 목록 | `pages/company/list/index.page.tsx` | `company/controller/CompanyController.java`, `CompanyService.java` | `feature/company/ui/list/company_list_screen.dart` | `company`, `company_keyword` |
| 회사 상세 | `pages/company/detail/[companyId].page.tsx`, `detail/part/*` | `CompanyController.java`, `CompanyService.java` | `feature/company/ui/detail/company_detail_screen.dart` | `company`, `company_review`, `position`, `jd` |
| 커뮤니티 목록 | `pages/community/index.page.tsx` | `community/controller/QnaController.java`, `QnaService.java` | `feature/community/ui/main/community_screen.dart` | `qna` |
| QnA 상세 | `pages/community/detail/[qnaId].page.tsx`, `detail/part/*` | `QnaController.java`, `QnaCommentController.java` | `feature/community/ui/detail/community_detail_screen.dart` | `qna`, `qna_comment`, `qna_comment_reply` |
| 커뮤니티 프로필 | `pages/community/profile/index.page.tsx` | `UserController.java` / QnA 연동 | `feature/community/ui/user/*` | `qna`, `user` |
| 마이페이지 | `pages/mypage/index.page.tsx`, `mypage/part/*`, `mypage/constant.tsx` | `user/controller/UserController.java`, `UserService.java` | `feature/user/ui/main/user_screen.dart` | `user`, `user_role`, `user_policy`, `user_alarm_config` + 아래 탭별 |
| ├ 프로필·계정 | `part/ProfileAndAccountPart` | `UserProfileController.java` | (동일 user) | `user`, `user_resume_profile`, `user_resume_profile_address`, `auth_crt` |
| ├ 내 스펙 | `part/SpecPart` | `SpecController.java` | `speclab` | `spec`, `spec_career` |
| ├ 지원내역 | `part/ApplyStatusPart` | `UserJdApplyController.java`, `JdApplicationController.java` | `feature/apply/ui/history/apply_history_screen.dart` | `jd_application`, `jd_applicant`, `jd_process` |
| ├ 포지션 제안 | `part/PositionRecommendPart` | `RecruitPositionController.java` | `feature/position/ui/proposal/position_proposal_screen.dart` | `recruit_position`, `recruit_position_candidate` |
| ├ 결제관리 | `part/PaymentPart` | `UserOrderController.java`, `OrderController.java` | `feature/payment/.../order_history.dart` | `order`, `order_payment`, `order_cart`, `order_cart_item` |
| ├ 멘토 북마크 | `part/MentorBookmarkPart` | `MentorBookmarkController.java`, `MentoringController.java` | `speclab` | `mentor_bookmark`, `mentor` |
| ├ 스크랩 | `part/ScrapPart` | `UserBookmarkController.java` | `feature/bookmark/main/bookmark_screen.dart` | `jd_bookmark`, `feed_bookmark` |
| ├ 커뮤니티(마이) | `part/CommunityPart` | `UserQnaController.java` | — | `qna`, `user` |
| ├ 멘토링 탭 | `?type=mentoring`, `MentoringListPart` | `MentoringController.java` | `speclab/presentation/pages/mentoring*.dart` | `mentoring`, `mentoring_item`, `mentor` |
| 멘토링 목록 | `pages/mentoring/index.page.tsx` | `MentoringController.java`, `MentoringService.java` | `speclab/.../mentoring.dart` | `mentor`, `mentoring`, `mentoring_item` |
| 멘토 상세 | `pages/mentoring/detail/[mentorId].page.tsx`, `detail/parts/*` | `MentoringController.java`, `MentorController.java` | `mentoring_detail.dart` | `mentor`, `mentor_career`, `mentor_file`, `mentoring` |
| 스펙랩 메인(웹) | `pages/speclab/main/index.page.tsx` | `SpecController.java`, `FeedbackService.java` 등 | `speclab_screen.dart` | `spec`, `mentoring`, `feedback`, `guidebook` (화면별) |
| 스펙 입력(웹) | `pages/spec/create/index.page.tsx`, `step1`~`step3-2`, `intro`, `complete` | `spec/controller/SpecController.java`, `SpecService.java` | `spec_*_form.dart`, `spec_input_intro/complete.dart` | `spec`, `spec_career`, `position_scoring_rule` |
| 스펙 리포트 | `pages/spec-report/index.page.tsx`, `preview`, `result` | `product/controller/SpecReportController.java`, `SpecReportService.java` | `my_spec.dart`, `pdf_viewer.dart`, `payment_provider` | `spec_report`, `spec_report_item`, `spec_report_item_statistics` |
| 이력서(웹) | `pages/resume/index.page.tsx`, `[resumeId]`, `complete`, `coverletter` | `resume/controller/ResumeController.java`, `ResumeService.java` | `feature/resume/ui/**`, `resume_routes.dart` | `resume`, `resume_career`, `resume_education`, `resume_certification`, `resume_cover_letter`, `resume_qualification`, … |
| 포지션 제안(단독) | `pages/proposal/index.page.tsx` | `RecruitPositionController.java` | `position_proposal_screen.dart` | `recruit_position`, `recruit_position_candidate` |
| 스펙 피드백 | `pages/feedback/index.page.tsx`, `detail/[feedId]` | `feed/controller/FeedbackController.java`, `FeedbackService.java` | `speclab/.../feedback/*.dart` | `feedback`, `feedback_like`, `feedback_view`, `feedback_report` |
| 내 피드백 | `pages/feedback/myFeedback/index.page.tsx` | `FeedbackController.java` | `my_feedback.dart` | `feedback`, `user` |
| 가이드북 | `pages/guide-book/index.page.tsx`, `view/index.page.tsx` | `company/controller/GuidebookController.java`, `GuidebookService.java` | `insight/.../insight_guide_*` 또는 `speclab/guide_book/*` | `guidebook`, `guidebook_access` |
| 멤버십 | `pages/membership/index.page.tsx` | `subscription/controller/SubscriptionController.java`, `PlanController.java` | `membership/presentation/pages/membership_page.dart` | `plan`, `subscription`, `order`, `webhook_inbox`, `outbox_event` |
| 구독 성공/실패 | `pages/subscription/success`, `fail` | `SubscriptionController.java`, `PaymentController.java` | `payment_result.dart` | `subscription`, `order`, `order_payment` |
| 회원가입 | `pages/signup/process/index.page.tsx` | `UserController.java`, `GuestUserController.java` | `auth/ui/update/register_survey/*`, `terms_agree_screen.dart` | `user`, `guest_user`, `user_register_survey`, `user_policy`, `guest_user_policy` |
| 로그인·JWT | `kakaologin.page.tsx`, `applelogin.page.tsx` | `jwt/controller/JwtController.java` | `auth/ui/sign_in/*` | `user`, `auth_crt` |
| 카카오 콜백 | `pages/kakao/index.page.tsx` | OAuth 연동 레이어 | — | `user`, `auth_crt` |
| 알림 | — | `user/controller/UserAlarmController.java` | `feature/alarm/ui/main/alarm_screen.dart` | `user_alarm` |
| 설정 | — | `UserController.java` | `feature/setting/ui/setting_screen.dart` | `user`, `user_policy`, `user_alarm_config` |
| 인사이트(앱) | — | `FeedController.java`, `BlogQueryService` 등 | `feature/insight/ui/**` | `feed`, `blog_post`, `feed_bookmark` |
| 챗봇 | — | `prompt/controller/PromptController.java` | `feature/chatbot/ui/chatbot_screen.dart` | `prompt` |
| 기업 리뷰 작성 | — | `company/controller/CompanyReviewController.java` | `feature/review/ui/upload/company_review_upload_screen.dart` | `company_incumbent_review` |
| 학교 검색 | — | `school/controller/SchoolController.java` | `feature/school/ui/school_search_screen.dart` | `school` |
| PASS 인증 | — | `oauth2/pass/controller/PassController.java` | `auth/ui/pass/*` | `pass_certification_file`, `user_certification` |
| 404/500 | `pages/404`, `500` | — | `feature/error/not_found_screen.dart` | — |

---

## 도메인별 테이블 묶음 (JPA 기준)

### 사용자 · 인증
`user`, `user_role`, `user_policy`, `user_alarm`, `user_alarm_config`, `user_register_survey`, `user_resume_profile`, `user_resume_profile_address`, `user_cover_letter`, `user_career`, `user_certification`, `user_jd_filter`, `user_place_code`, `user_blind_company`, `user_block`, `user_report`, `guest_user`, `guest_user_policy`, `experience`, `user_work_condition`, `user_coupon`, `auth_crt`

### JD · 지원
`jd`, `jd_bookmark`, `jd_view`, `jd_click`, `jd_cover_letter`, `jd_applicant`, `jd_application`, `jd_application_survey`, `jd_application_target_company`, `jd_process`, `jd_place`, `jd_place_address`, `jd_attachment`, `jd_alarm`, `jd_rank`, `pass_certification_file`

### 회사 · 포지션 · 가이드
`company`, `company_review`, `company_incumbent_review`, `position`, `guidebook`, `guidebook_access`, `company_keyword`

### 커뮤니티
`qna`, `qna_comment`, `qna_comment_reply`

### 이력서
`resume`, `resume_career`, `resume_education`, `resume_certification`, `resume_cover_letter`, `resume_qualification`, `resume_activity`, `resume_fluency`, `resume_memo`, `resume_view`, `resume_bookmark`, `resume_attendance`

### 스펙 · 리포트
`spec`, `spec_career`, `position_scoring_rule`, `spec_report`, `spec_report_item`, `spec_report_item_statistics`

### 멘토링 · 상품
`mentor`, `mentor_career`, `mentor_file`, `mentor_bookmark`, `mentor_report`, `settlement`, `mentoring`, `mentoring_item`, `mentoring_mentoring_item`, `mentoring_review`, `campaign`, `campaign_item`, `campaign_item_catalog`, `campaign_statistics`, `human_pool`, `human_pool_item`

### 피드백 · 콘텐츠
`feedback`, `feedback_like`, `feedback_view`, `feedback_report`, `feed`, `feed_bookmark`, `blog_post`, `notice`, `notice_view`

### 포지션 제안
`recruit_position`, `recruit_position_candidate`

### 결제 · 구독 · 장바구니
`order`, `order_payment`, `order_cart`, `order_cart_item`, `plan`, `subscription`, `subscription_statistics`, `webhook_inbox`, `outbox_event`, `credit_transaction`, `point_transaction`

### 배너 · 검색 · 기타
`banner_statistics`, `search_keyword`, `school`, `showcase_posting`, `showcase_posting_statistics`, `s3_deletion_queue`, `sales_statistics`, `partnership`, `partnership_verification`, `partnership_verification_file`

---

## 에이전트용 빠른 분기

| 증상 | 코드 | DB |
|------|------|------|
| 북마크 숫자 이상 | JD: `JdFooterPart` / App `jd_detail_controller` | `jd_bookmark`, `mentor_bookmark` |
| 지원 불가/상태 이상 | `JdApplication*` API | `jd_application`, `jd_applicant`, `jd_process` |
| 결제는 됐는데 이용 불가 | `Subscription*`, `Order*` | `subscription`, `order`, `order_payment`, `webhook_inbox` |
| 스펙 저장 안 됨 | `spec/create`, `SpecController` | `spec`, `spec_career` |
| 리포트 안 보임 | `spec-report`, `SpecReportController` | `spec_report`, `spec_report_item` |

---

## 관련 문서

- `deeple-context/shared/db-guide.md` — MCP MySQL, 테이블 도메인 요약, 쿼리 예시  
- `deeple-context/dmand/cs/AGENTS.md` — CS 스킬 구조 및 사용 흐름
