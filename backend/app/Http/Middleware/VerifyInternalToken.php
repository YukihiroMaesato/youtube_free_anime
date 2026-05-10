<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class VerifyInternalToken
{
    public function handle(Request $request, Closure $next): Response
    {
        $token = $request->header('X-Internal-Token');

        if ($token !== env('PYTHON_INTERNAL_API_TOKEN')) {
            abort(403, 'Forbidden');
        }

        return $next($request);
    }
}
