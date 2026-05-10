<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use App\Models\YoutubeChannel;
use App\Models\AnimeTitle;
use App\Models\Tag;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Video extends Model
{
    use SoftDeletes;

    protected $guarded = [];

    protected $casts = [
        'published_at' => 'datetime',
        'free_until_at' => 'datetime',
        'fetched_at' => 'datetime',

        'is_free' => 'boolean',
        'is_official' => 'boolean',

        'ai_result' => 'array',
    ];

    public function youtubeChannel(): BelongsTo
    {
        return $this->belongsTo(YoutubeChannel::class);
    }
 
    public function animeTitle(): BelongsTo
    {
        return $this->belongsTo(AnimeTitle::class);
    }
 
    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class, 'video_tags');
    }
}