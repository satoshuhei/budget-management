# 部門内 予算管理システム

## セットアップ

1. 仮想環境を作成して有効化
2. 依存関係をインストール

3. 環境変数を用意

```
copy .env.example .env
```

4. DBを起動

```
docker compose up -d
```

5. マイグレーション

```
alembic upgrade head
```

## 起動

```
uvicorn app.main:app --reload
```

OpenAPI: http://127.0.0.1:8000/docs

### フロントエンド

```
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## フロントエンド起動

```
cd frontend
npm install
npm run dev
```

http://localhost:5173

## 簡易ログイン（ダミー認証）

```
POST /api/auth/login
{
	"username": "alice",
	"password": "password"
}
```

成功すると role が返るので、以降はヘッダーで指定します。

- X-User: alice
- X-Role: USER

## CSVインポート（年度計画）

ヘッダー（1行目）:

fiscal_year,department_id,category_id,subcategory_id,product_name,vendor,planned_month,contract_type,amount,plan_type,note

例:

2026,1,10,11,Service A,Vendor X,2026-04,月額,1200,サブスク,初期登録

## テスト

```
pytest
```

## MVP1 実装状況

- 予算枠（Budget）登録
- 予算補正（Adjustment）
- 年度計画（Plan）CRUD（作成/更新）
- 計画変更履歴（PlanChange）
- ドメインルールのテスト（残予算計算/引当・実績/ステータス遷移）

## 次に実装予定

- Plan一覧/検索API
- 申請（Request）起票/承認/差戻し
- 引当（Commit）/実績（Actual）取引
- ダッシュボード集計API
- 監査ログ
# budget-management