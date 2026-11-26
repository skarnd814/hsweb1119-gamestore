# 🎮 GameStore

스팀 인기 게임 8개를 파는 게임 판매 사이트입니다.
한신대학교 「웹프로그래밍(AS006-E)」 수업 실습으로 만들었고, Supabase 데이터베이스와 연결되어 있습니다.

- **사이트:** https://skarnd814.github.io/hsweb1119-gamestore/
- **관리 페이지:** https://skarnd814.github.io/hsweb1119-gamestore/admin.html (관리자 계정만)

> ⚠ 수업 실습용 사이트입니다. 회원가입과 주문은 데이터베이스에 저장되지만, 실제 결제 · 포인트 지급 · 게임 다운로드는 이루어지지 않습니다.
> 게임 이름과 가격은 예시이며, 각 게임의 권리는 해당 개발사와 퍼블리셔에 있습니다.

## 주요 기능

| 구분 | 기능 |
|---|---|
| 화면 | 도트 그림 히어로 슬라이드 4장(교차 페이드), 오른쪽 위 주컬러 테마 5종, 모바일 화면 대응 |
| 상품 | `shop_products` 에서 판매 중인 게임을 읽음 · 분류 탭(표의 category) · 할인 중 · 이름 검색 · 상세 · 품절 표시 |
| 회원 | Supabase Auth 회원가입(이름 · 연락처) · 로그인 · 로그아웃, 메뉴에 「이름 님」, 마이페이지(이름 · 연락처 수정, 주문 내역) |
| 멤버십 | 브론즈 1% · 실버 3% · 골드 5% · 다이아 8% · 레전드 10% 적립, 가입 축하 1,000P |
| 주문 | 결제하면 `shop_orders` 와 `shop_order_items` 에 저장 (합계 = 수량 × 단가의 합), 완료 화면에 주문 번호 |
| 관리 | 회원 수 · 주문 건수 · 주문 합계 · 등급별 인원, 회원 등급 · 포인트 · 역할 수정, 주문 상태 변경 |

## 파일 구성

```
index.html          쇼핑몰 (CSS · JS 포함 한 파일)
admin.html          회원 · 주문 관리 페이지 (관리자만)
db.js               Supabase 연결 (Project URL + Publishable key, 연결 변수 db)
shop_supabase.sql   표 4개 · 보안 규칙 · 함수 · 게임 8개를 만드는 SQL
img/                게임 표지 8장 · 히어로 배경 4장 (직접 그린 도트 그림)
Tools/SpriteGen/    도트 그림을 만든 생성기
```

모든 html 은 `supabase-js(CDN) → db.js → 페이지 스크립트` 순서로 불러옵니다.

## 데이터베이스 (Supabase · 접두어 `shop_`)

| 표 | 한 줄이 뜻하는 것 | 주요 열 |
|---|---|---|
| `shop_profiles` | 회원 한 명 | email · name · phone · grade(BRONZE~LEGEND) · points · role(member/admin) |
| `shop_products` | 게임 한 개 | name · name_ko · developer · category · price · sale(할인율 %) · stock · image_url · is_active |
| `shop_orders` | 주문 한 건 | user_id · total · status(결제완료 · 배송중 · 배송완료 · 취소) |
| `shop_order_items` | 주문에 담긴 게임 | order_id · product_id · qty · unit_price |

수업 원본 SQL 에서 바꾼 곳: 등급 5단계(BRONZE · SILVER · GOLD · DIAMOND · LEGEND), 가입 포인트 1,000, 상품 표에 `name_ko` · `developer` · `sale` 열 추가.

### 보안 규칙 (RLS)

- **방문자**: 판매 중인 게임만 읽을 수 있고, 회원 · 주문 표는 볼 수 없습니다.
- **회원**: 내 정보와 내 주문만 보고, 이름 · 연락처만 고칠 수 있습니다. 등급 · 포인트 · 역할은 바꿀 수 없습니다.
- **관리자**: 모든 회원 · 주문을 보고, 등급 · 포인트 · 역할은 `shop_admin_update_member` 함수로만 바꿉니다.

사이트 파일에는 공개해도 되는 **Project URL** 과 **Publishable key** 만 들어 있습니다. Secret key 와 DB 비밀번호는 어디에도 넣지 않습니다.

## 직접 설치해 보기

1. Supabase 에서 새 프로젝트를 만들고 **SQL Editor** 에서 `shop_supabase.sql` 전체를 실행합니다.
2. **Authentication → Sign In / Providers** 에서 실습 동안 **Confirm email** 을 끕니다. (실제 서비스에서는 다시 켭니다)
3. `db.js` 의 `SUPABASE_URL` 과 `SUPABASE_KEY` 를 내 프로젝트의 Project URL · Publishable key 로 바꿉니다.
4. 저장소를 GitHub Pages(main 브랜치)로 배포합니다.
5. 사이트에서 가입한 뒤 SQL Editor 에서 내 계정을 관리자로 지정합니다.
   ```sql
   UPDATE public.shop_profiles SET role = 'admin' WHERE email = '가입한 이메일';
   ```

## 만든 도구

HTML · CSS · JavaScript, Supabase(PostgreSQL · Auth · RLS), supabase-js, GitHub Pages, Python(도트 그림 생성)
