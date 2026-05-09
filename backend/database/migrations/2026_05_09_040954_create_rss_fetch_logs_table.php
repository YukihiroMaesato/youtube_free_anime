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
        Schema::create('rss_fetch_logs', function (Blueprint $table) {
            $table->id();

            $table->foreignId('youtube_channel_id')
                ->constrained()
                ->cascadeOnDelete();

            // 取得件数
            $table->integer('fetched_count')
                ->default(0);

            // 成功したか
            $table->boolean('success')
                ->default(true);

            // エラー内容
            $table->text('error_message')
                ->nullable();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('rss_fetch_logs');
    }
};
