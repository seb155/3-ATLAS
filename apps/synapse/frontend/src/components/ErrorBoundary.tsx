import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error,
            errorInfo
        });
    }

    private handleReload = () => {
        window.location.reload();
    };

    private handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
    };

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
                    <div className="max-w-lg w-full bg-slate-900 border border-slate-800 rounded-lg p-8 shadow-xl">
                        <div className="flex items-start gap-4">
                            <div className="flex-shrink-0">
                                <svg
                                    className="w-8 h-8 text-red-500"
                                    fill="none"
                                    strokeWidth="2"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                    />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold text-white mb-2">
                                    Something went wrong
                                </h3>
                                <p className="text-slate-400 text-sm mb-4">
                                    An unexpected error occurred. You can try reloading the page or resetting the component.
                                </p>

                                {process.env.NODE_ENV === 'development' && this.state.error && (
                                    <details className="mb-4 bg-slate-950 border border-slate-800 rounded p-3">
                                        <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-400">
                                            Error Details (Development Only)
                                        </summary>
                                        <pre className="mt-2 text-xs text-red-400 overflow-auto">
                                            {this.state.error.toString()}
                                            {this.state.errorInfo && (
                                                <>
                                                    {'\n\n'}
                                                    {this.state.errorInfo.componentStack}
                                                </>
                                            )}
                                        </pre>
                                    </details>
                                )}

                                <div className="flex gap-2">
                                    <button
                                        onClick={this.handleReload}
                                        className="px-4 py-2 bg-mining-teal text-white rounded hover:bg-mining-teal/90 transition-colors text-sm font-medium"
                                    >
                                        Reload Page
                                    </button>
                                    <button
                                        onClick={this.handleReset}
                                        className="px-4 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 transition-colors text-sm font-medium"
                                    >
                                        Try Again
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
