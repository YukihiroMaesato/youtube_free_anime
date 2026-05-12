<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class VideoTitleIndexRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'q' => ['sometimes', 'string', 'max:100'],
            'all' => ['sometimes', 'boolean'],
        ];
    }
}
