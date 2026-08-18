import React, { useState, useCallback } from 'react';
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { uploadFile } from '@/services/api/upload';

interface FileUploaderProps {
    onUploadSuccess: (documentId: number, fileName: string) => void;
    onUploadError?: (error: string) => void;
    accept?: string;
    maxSize?: number; // in bytes
}

export const FileUploader: React.FC<FileUploaderProps> = ({
    onUploadSuccess,
    onUploadError,
    accept = '.docx,.pdf,.doc,.txt',
    maxSize = 10 * 1024 * 1024,
}) => {
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const handleUpload = useCallback(async (file: File) => {
        // File size validation
        if (file.size > maxSize) {
            const errorMsg = `文件大小超过限制 (最大 ${Math.round(maxSize / 1024 / 1024)}MB)`;
            message.error(errorMsg);
            onUploadError?.(errorMsg);
            return false;
        }

        // File type validation
        const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
        const acceptList = accept.split(',').map(ext => ext.trim().toLowerCase());
        if (!acceptList.includes(fileExtension)) {
            const errorMsg = `不支持的文件格式。支持的格式: ${accept}`;
            message.error(errorMsg);
            onUploadError?.(errorMsg);
            return false;
        }

        setUploading(true);
        setUploadProgress(0);

        try {
            const data = await uploadFile(file);

            setUploadProgress(100);
            message.success('文件上传成功!');

            onUploadSuccess(data.document_id, data.file_name || file.name);

        } catch (error: unknown) {
            const errorMsg = error instanceof Error ? error.message : '文件上传失败';
            message.error(errorMsg);
            onUploadError?.(errorMsg);
        } finally {
            setUploading(false);
            setUploadProgress(0);
        }

        return false; // Prevent default upload behavior
    }, [accept, maxSize, onUploadSuccess, onUploadError]);

    return (
        <Upload
            accept={accept}
            beforeUpload={handleUpload}
            showUploadList={false}
            disabled={uploading}
        >
            <Button
                icon={<UploadOutlined />}
                loading={uploading}
                disabled={uploading}
            >
                {uploading ? `上传中... ${uploadProgress}%` : '上传文件'}
            </Button>
        </Upload>
    );
};
