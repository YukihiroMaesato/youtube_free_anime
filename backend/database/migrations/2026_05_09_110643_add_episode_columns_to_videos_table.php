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
        Schema::table('videos', function (Blueprint $table) {

            // 単話番号
            $table->integer('episode_number')
                ->nullable()
                ->after('video_type')
                ->index()
                ->comment('単話番号');

            // 一挙開始話数
            $table->integer('episode_start')
                ->nullable()
                ->after('episode_number')
                ->comment('一挙開始話数');

            // 一挙終了話数
            $table->integer('episode_end')
                ->nullable()
                ->after('episode_start')
                ->comment('一挙終了話数');

            // シーズン番号
            $table->integer('season_number')
                ->nullable()
                ->after('episode_end')
                ->index()
                ->comment('シーズン番号');

        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('videos', function (Blueprint $table) {
            //
        });
    }
};
