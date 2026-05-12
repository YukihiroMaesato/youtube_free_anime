<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VideoController;
use App\Http\Controllers\Internal\VideoController as InternalVideoController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::get('/health', function () {
    return response()->json(['status' => 'ok eee']);
});

Route::get('/videos', [VideoController::class, 'index']);
Route::get('/videos/tags', [VideoController::class, 'tags']);
Route::get('/videos/titles', [VideoController::class, 'titles']);

Route::middleware('internal.token')
    ->prefix('internal')
    ->group(function () {

        Route::get('/videos/showMany', [InternalVideoController::class, 'showMany']);

        Route::post('/videos/bulk-store', [InternalVideoController::class, 'bulkStore']);
    });
