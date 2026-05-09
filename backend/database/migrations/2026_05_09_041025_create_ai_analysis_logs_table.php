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
        Schema::create('ai_analysis_logs', function (Blueprint $table) {
            $table->id();

            $table->foreignId('video_id')
                ->constrained()
                ->cascadeOnDelete();

            // AIモデル名
            $table->string('model_name')->comment('AIモデル名');

            // AI入力
            $table->longText('input_text')->comment('AI入力');

            // AI出力
            $table->json('output_json')->comment('AI出力');

            // 実行時間
            $table->integer('processing_ms')
                ->nullable()->comment('実行時間(ms)');

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('ai_analysis_logs');
    }
};
