<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\YoutubeChannel;

class YoutubeChannelSeeder extends Seeder
{
    public function run(): void
    {
        $path = database_path('seeders/data/youtube_channels.csv');

        $file = fopen($path, 'r');

        /*
        |--------------------------------------------------------------------------
        | ヘッダー取得
        |--------------------------------------------------------------------------
        */

        $headers = fgetcsv($file);

        while (($row = fgetcsv($file)) !== false) {

            $data = array_combine($headers, $row);

            YoutubeChannel::updateOrCreate(
                [
                    'id' => $data['id'],
                ],
                [
                    'youtube_channel_id' => $data['youtube_channel_id'],
                    'name'               => $data['name'],
                    'url'                => $data['url'],
                    'is_official'        => filter_var(
                        $data['is_official'],
                        FILTER_VALIDATE_BOOLEAN
                    ),
                    'country_code'       => $data['country_code'] ?: null,
                ]
            );
        }

        fclose($file);
    }
}