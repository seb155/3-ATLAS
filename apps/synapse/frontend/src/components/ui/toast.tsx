import toast, { Toaster } from 'react-hot-toast';

// Toast configuration
export const toastConfig = {
    duration: 4000,
    position: 'bottom-right' as const,
    style: {
        background: '#1e293b', // slate-800
        color: '#f1f5f9', // slate-100
        border: '1px solid #334155', // slate-700
        borderRadius: '0.5rem',
        fontSize: '0.875rem',
        padding: '12px 16px',
    },
    success: {
        iconTheme: {
            primary: '#14b8a6', // mining-teal
            secondary: '#f1f5f9',
        },
    },
    error: {
        iconTheme: {
            primary: '#ef4444', // red-500
            secondary: '#f1f5f9',
        },
    },
};

// Toast Component (to be placed at app root)
export const ToastProvider = () => {
    return (
        <Toaster
            position={toastConfig.position}
            toastOptions={toastConfig}
        />
    );
};

// Helper functions for easy toast usage
export const showToast = {
    success: (message: string) => {
        toast.success(message);
    },

    error: (message: string) => {
        toast.error(message);
    },

    info: (message: string) => {
        toast(message, {
            icon: '💡',
        });
    },

    loading: (message: string) => {
        return toast.loading(message);
    },

    promise: <T,>(
        promise: Promise<T>,
        messages: {
            loading: string;
            success: string | ((data: T) => string);
            error: string | ((error: unknown) => string);
        }
    ) => {
        return toast.promise(promise, messages);
    },

    dismiss: (toastId?: string) => {
        toast.dismiss(toastId);
    },
};

export default toast;
