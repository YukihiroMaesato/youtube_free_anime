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
        Schema::create('anime_titles', function (Blueprint $table) {
            $table->id();

            // 作品タイトル
            $table->string('title')->comment('作品タイトル');

            // AIや正規化後タイトル
            // 検索用
            $table->string('normalized_title')->index()->comment('AIや正規化後タイトル');

            // かな
            $table->string('title_kana')->nullable()->comment('かな');

            // 英語タイトル
            $table->string('title_en')->nullable()->comment('英語タイトル');

            // 放送年
            $table->integer('season_year')->nullable()->comment('放送年');

            // season:
            // spring/summer/autumn/winter
            $table->string('season_name', 20)->nullable()->comment('シーズン名');

            // 公式サイト
            $table->text('official_site')->nullable()->comment('公式サイト');

            $table->timestamps();

            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('anime_titles');
    }
};
