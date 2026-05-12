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
            'video_type' => ['sometimes', 'string', 'max:50'],
        ];
    }
}
