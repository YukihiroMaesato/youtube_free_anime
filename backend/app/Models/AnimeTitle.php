<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Relations\HasMany;
 
class AnimeTitle extends Model
{
    use SoftDeletes;
 
    protected $guarded = [];
 
    public function videos(): HasMany
    {
        return $this->hasMany(Video::class);
    }
}