<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('videos', function (Blueprint $table) {
            $table->id();

            // どの作品か
            $table->foreignId('anime_title_id')
                ->nullable()
                ->constrained()
                ->nullOnDelete()
                ->comment('どの作品か');

            // どのチャンネルか
            $table->foreignId('youtube_channel_id')
                ->constrained()
                ->cascadeOnDelete()
                ->comment('どのチャンネルか');

            // YouTube動画ID
            // embedに使う
            $table->string('youtube_video_id')
                ->unique()
                ->comment('YouTube動画ID');

            // 動画タイトル
            $table->string('title')
                ->comment('動画タイトル');

            // 正規化タイトル
            $table->string('normalized_title')
                ->nullable()
                ->index()
                ->comment('AIや正規化後タイトル');

            // 動画説明欄
            $table->longText('description')
                ->nullable()
                ->comment('動画説明欄');

            // サムネURL
            $table->text('thumbnail_url')
                ->nullable()
                ->comment('サムネURL');

            // YouTube公開日時
            $table->timestamp('published_at')
                ->comment('YouTube公開日時');

            // 秒数
            $table->integer('duration_seconds')
                ->nullable()
                ->comment('秒数');

            // 動画種類
            // episode/pv/op/ed/movie/live
            $table->string('video_type', 50)
                ->nullable()
                ->index()
                ->comment('動画種類');

            // 言語
            $table->string('language_code', 10)
                ->nullable()
                ->comment('言語');

            // 無料公開か
            $table->boolean('is_free')
                ->default(true)
                ->index()
                ->comment('無料公開か');

            // 公式動画か
            $table->boolean('is_official')
                ->default(true)
                ->comment('公式動画か');

            // AIスコア
            // 信頼度
            $table->decimal('ai_score', 5, 2)
                ->nullable()
                ->comment('AIスコア');

            // AI結果JSON
            $table->json('ai_result')
                ->nullable()
                ->comment('AI結果JSON');

            // RSS取得日時
            $table->timestamp('fetched_at')
                ->nullable()
                ->comment('RSS取得日時');

            $table->timestamps();

            // 公開終了時に論理削除
            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('videos');
    }
};
