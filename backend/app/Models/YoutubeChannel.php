<?php
 
namespace App\Models;
 
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Relations\HasMany;
 
class YoutubeChannel extends Model
{
    use SoftDeletes;

    protected $table = 'youtube_channels';
 
    protected $guarded = [];
 
    protected $casts = [
        'is_official'    => 'boolean',
        'last_fetched_at' => 'datetime',
    ];
 
    public function videos(): HasMany
    {
        return $this->hasMany(Video::class, 'youtube_channel_id', 'id');
    }
}