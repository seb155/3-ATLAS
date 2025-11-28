import { useNavigate, useParams } from 'react-router-dom';
import { useCallback } from 'react';

/**
 * Hook for asset navigation using React Router
 * Provides clean URLs and standard navigation patterns
 */
export const useAssetNavigation = () => {
    const navigate = useNavigate();
    const params = useParams();

    const navigateToAsset = useCallback((assetId: string) => {
        // Navigate to asset detail route
        navigate(`/engineering/assets/${assetId}`);
    }, [navigate]);

    const navigateToEngineering = useCallback(() => {
        navigate('/engineering');
    }, [navigate]);

    const currentAssetId = params.assetId;

    return {
        navigateToAsset,
        navigateToEngineering,
        currentAssetId,
    };
};
