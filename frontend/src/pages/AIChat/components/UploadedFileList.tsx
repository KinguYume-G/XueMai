import React from 'react';
import { List, Popconfirm, Button, Empty } from 'antd';
import { FileTextOutlined, FilePdfOutlined, FileWordOutlined, DeleteOutlined } from '@ant-design/icons';

interface UploadedFile {
    id: number;
    name: string;
    size: number;
    uploadedAt: string;
}

interface UploadedFileListProps {
    files: UploadedFile[];
    onRemove?: (fileId: number) => void;
    maxDisplay?: number;
}

// Utility function to format file size
const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

// Get file icon based on extension
const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
        case 'pdf':
            return <FilePdfOutlined style={{ fontSize: '20px', color: '#ff4d4f' }} />;
        case 'doc':
        case 'docx':
            return <FileWordOutlined style={{ fontSize: '20px', color: '#1890ff' }} />;
        default:
            return <FileTextOutlined style={{ fontSize: '20px', color: '#8c8c8c' }} />;
    }
};

export const UploadedFileList: React.FC<UploadedFileListProps> = ({
    files,
    onRemove,
    maxDisplay = 5,
}) => {
    const displayFiles = files.slice(0, maxDisplay);

    if (files.length === 0) {
        return (
            <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无上传文件"
                style={{ padding: '20px 0' }}
            />
        );
    }

    return (
        <List
            dataSource={displayFiles}
            renderItem={(file) => (
                <List.Item
                    key={file.id}
                    style={{
                        padding: '12px 16px',
                        cursor: 'default',
                        transition: 'background-color 0.3s',
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#f5f5f5';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                    actions={
                        onRemove
                            ? [
                                <Popconfirm
                                    key="delete"
                                    title="确定要删除此文件吗?"
                                    onConfirm={() => onRemove(file.id)}
                                    okText="删除"
                                    cancelText="取消"
                                    okButtonProps={{ danger: true }}
                                >
                                    <Button
                                        type="text"
                                        danger
                                        icon={<DeleteOutlined />}
                                        size="small"
                                    >
                                        删除
                                    </Button>
                                </Popconfirm>,
                            ]
                            : undefined
                    }
                >
                    <List.Item.Meta
                        avatar={getFileIcon(file.name)}
                        title={
                            <span style={{ fontSize: '14px', fontWeight: 500 }}>
                                {file.name}
                            </span>
                        }
                        description={
                            <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
                                {formatFileSize(file.size)}
                            </span>
                        }
                    />
                </List.Item>
            )}
            bordered
            style={{ backgroundColor: '#fff' }}
        />
    );
};
