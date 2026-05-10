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
        Schema::table('video_tags', function (Blueprint $table) {
            $table->foreignId('video_id')
                ->after('id')
                ->constrained()
                ->cascadeOnDelete()
                ->comment('動画ID');

            $table->foreignId('tag_id')
                ->after('video_id')
                ->constrained()
                ->cascadeOnDelete()
                ->comment('タグID');

            $table->unique(['video_id', 'tag_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('video_tags', function (Blueprint $table) {
            //
        });
    }
};
