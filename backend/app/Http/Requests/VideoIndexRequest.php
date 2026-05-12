<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class VideoIndexRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'page' => ['sometimes', 'integer', 'min:1'],
            'tag_id' => ['sometimes', 'integer', 'exists:tags,id'],
            'anime_title_id' => ['sometimes', 'integer', 'exists:anime_titles,id'],
            'video_type' => ['sometimes', 'string', 'max:50'],
        ];
    }
}
