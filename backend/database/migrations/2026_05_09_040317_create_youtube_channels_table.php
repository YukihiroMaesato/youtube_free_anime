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
        Schema::create('youtube_channels', function (Blueprint $table) {
            $table->id();

            // YouTube公式のチャンネルID
            // 例: UC7Pl...
            $table->string('youtube_channel_id')->unique()->comment('YouTube公式のチャンネルID');

            // チャンネル名
            $table->string('name')->comment('チャンネル名');

            // チャンネルURL
            $table->text('url')->comment('チャンネルURL');

            // 公式チャンネルか
            $table->boolean('is_official')->default(true)->comment('公式チャンネルか');

            // 国コード
            // JP, US など
            $table->string('country_code', 10)->nullable()->comment('国コード');

            // 最後にRSS取得した日時
            $table->timestamp('last_fetched_at')->nullable()->comment('最後にRSS取得した日時');

            $table->timestamps();

            // 論理削除
            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('youtube_channels');
    }
};
